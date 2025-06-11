from __future__ import annotations

import json
from typing import Dict, Any

from django.db.models import Q
from django.http import HttpResponse

from apps.pages.models import Book, PastPaper, Department, Student, ChatSession
from apps.pages.whatsapp.utils.whatsapp import (
    send_whatsapp_message,
    send_whatsapp_list_message,
)

# ---------------------------------------------------------------------------
# Helpers for interactive lists
# ---------------------------------------------------------------------------

def _list_rows_from_queryset(qs, *, id_field: str = "id", title_field: str = "name", desc_field: str | None = None):
    """Convert queryset to WhatsApp list‑row dicts."""
    rows = []
    for obj in qs:
        row = {
            "id": str(getattr(obj, id_field)),
            "title": getattr(obj, title_field),
        }
        if desc_field:
            row["description"] = getattr(obj, desc_field)
        rows.append(row)
    return rows

# ---------------------------------------------------------------------------
# Menu sending functions
# ---------------------------------------------------------------------------

def send_library_menu(phone_number_id: str, to: str) -> None:
    """Send the main library menu (interactive list)."""
    sections = [
        {
            "title": "📚 Library Menu",
            "rows": [
                {
                    "id": "library_search_books",
                    "title": "🔍 Search Books",
                    "description": "Search books by title, author, ISBN, or department.",
                },
                {
                    "id": "library_search_papers",
                    "title": "📝 Search Past Papers",
                    "description": "Find past papers by department & year.",
                },
                {
                    "id": "library_my_borrowed",
                    "title": "📖 My Borrowed Books",
                    "description": "View books you have currently borrowed.",
                },
                {
                    "id": "library_back_to_main",
                    "title": "🔙 Back to Main Menu",
                    "description": "Return to student portal menu.",
                },
            ],
        }
    ]
    send_whatsapp_list_message(
        phone_number_id,
        to,
        body="Welcome to the Library Management System. Please select an option:",
        sections=sections,
    )


def send_department_options(phone_number_id: str, to: str) -> None:
    """Send department list; uses department id to avoid duplicate‑name clash."""
    departments = Department.objects.all().order_by("name")
    sections = [
        {
            "title": "Departments",
            "rows": _list_rows_from_queryset(departments),
        }
    ]
    send_whatsapp_list_message(
        phone_number_id,
        to,
        body="Please select the department:",
        sections=sections,
    )


def send_year_options(phone_number_id: str, to: str) -> None:
    years = [
        {"id": "1", "title": "1st Year"},
        {"id": "2", "title": "2nd Year"},
        {"id": "3", "title": "3rd Year"},
        {"id": "4", "title": "4th Year"},
        {"id": "all", "title": "All Years"},
    ]
    sections = [
        {
            "title": "Academic Year",
            "rows": years,
        }
    ]
    send_whatsapp_list_message(
        phone_number_id,
        to,
        body="Please select the academic year:",
        sections=sections,
    )


def _send_department_disambiguation(phone_number_id: str, to: str, duplicates):
    """Ask user to pick exact department when duplicates exist."""
    rows = _list_rows_from_queryset(duplicates)
    send_whatsapp_list_message(
        phone_number_id,
        to,
        header="Multiple Departments Found",
        body="Please choose the exact department:",
        button_text="View Options",
        sections=[{"title": "Departments", "rows": rows}],
    )

# ---------------------------------------------------------------------------
# Main flow handler
# ---------------------------------------------------------------------------

def handle_library_flow(
    text: str,
    phone_number_id: str,
    from_number: str,
    session: ChatSession,
):


    # ------------------------------------------------------------------
    # 1. User enters library from student portal
    # ------------------------------------------------------------------
    if text == "student_library":
        # Ensure user is logged in
        try:
            Student.objects.get(reg_number=session.reg_number)
        except Student.DoesNotExist:
            session.stage = "awaiting_login"
            session.save()
            send_whatsapp_message(
                phone_number_id,
                from_number,
                "🔐 Please log in first by sending: `REG1234 yourpassword`",
            )
            return HttpResponse("Login required", status=200)

        session.stage = "library_menu"
        session.save()
        send_library_menu(phone_number_id, from_number)
        return HttpResponse("Library menu sent", status=200)

    # ------------------------------------------------------------------
    # 2. Library menu selections
    # ------------------------------------------------------------------
    if session.stage == "library_menu":
        if text == "library_search_books":
            session.stage = "library_search"
            session.save()
            send_whatsapp_message(
                phone_number_id,
                from_number,
                "📚 Please type the book title, author, ISBN, or department to search.",
            )
            return HttpResponse("Prompted book search", status=200)

        if text == "library_search_papers":
            session.stage = "past_paper_choose_department"
            session.data = {}
            session.save()
            send_department_options(phone_number_id, from_number)
            return HttpResponse("Sent department options", status=200)

        if text == "library_my_borrowed":
            return _send_borrowed_books(phone_number_id, from_number, session)

        if text == "library_back_to_main":
            session.stage = "student_portal_main"
            session.save()
            send_whatsapp_message(phone_number_id, from_number, "🔙 Returning to the main menu.")
            return HttpResponse("Returned to main menu", status=200)

        # Fallback inside menu
        send_whatsapp_message(phone_number_id, from_number, "⚠️ Invalid option. Please select from the list.")
        send_library_menu(phone_number_id, from_number)
        return HttpResponse("Invalid library option", status=200)

    # ------------------------------------------------------------------
    # 3. Book search stage
    # ------------------------------------------------------------------
    if session.stage == "library_search":
        if text in [
            "library_my_borrowed",
            "library_back_to_main",
            "library_menu",
        ]:
            # Re‑enter the menu flow
            session.stage = "library_menu"
            session.save()
            return handle_library_flow(text, phone_number_id, from_number, session)

        _perform_book_search(phone_number_id, from_number, text)
        return HttpResponse("Library search completed", status=200)

    # ------------------------------------------------------------------
    # 4. Past paper – choose department stage (+ disambiguation)
    # ------------------------------------------------------------------
    if session.stage == "past_paper_choose_department":
        # Try by ID first (if user selected from list)
        dept_qs = None
        if text.isdigit():
            dept_qs = Department.objects.filter(id=int(text))
        else:
            dept_qs = Department.objects.filter(name__iexact=text.strip())

        if not dept_qs.exists():
            send_whatsapp_message(phone_number_id, from_number, "⚠️ Invalid department. Please select from the list.")
            send_department_options(phone_number_id, from_number)
            return HttpResponse("Invalid department", status=200)

        if dept_qs.count() > 1:
            _send_department_disambiguation(phone_number_id, from_number, dept_qs)
            session.stage = "past_paper_disambiguate_dept"
            session.save()
            return HttpResponse("Ambiguous department", status=200)

        selected_department = dept_qs.first()
        session.data = {"past_paper_department_id": selected_department.id}
        session.stage = "past_paper_choose_year"
        session.save()
        send_year_options(phone_number_id, from_number)
        return HttpResponse("Sent year options", status=200)

    # ------------------------------------------------------------------
    # 4b. Disambiguation stage (user picks department id)
    # ------------------------------------------------------------------
    if session.stage == "past_paper_disambiguate_dept":
        if not text.isdigit():
            send_whatsapp_message(phone_number_id, from_number, "⚠️ Please select using the buttons provided.")
            return HttpResponse("Awaiting department id", status=200)
        try:
            selected_department = Department.objects.get(id=int(text))
        except Department.DoesNotExist:
            send_whatsapp_message(phone_number_id, from_number, "⚠️ Invalid selection.")
            return HttpResponse("Invalid department id", status=200)

        session.data = {"past_paper_department_id": selected_department.id}
        session.stage = "past_paper_choose_year"
        session.save()
        send_year_options(phone_number_id, from_number)
        return HttpResponse("Disambiguation complete", status=200)

    # ------------------------------------------------------------------
    # 5. Past paper – choose year
    # ------------------------------------------------------------------
    if session.stage == "past_paper_choose_year":
        year_filter = None
        if text.lower() != "all":
            try:
                year_filter = int(text)
                if year_filter not in [1, 2, 3, 4]:
                    raise ValueError
            except ValueError:
                send_whatsapp_message(phone_number_id, from_number, "⚠️ Please select a valid year (1‑4) or 'All'.")
                send_year_options(phone_number_id, from_number)
                return HttpResponse("Invalid year", status=200)

        department_id = session.data.get("past_paper_department_id")
        if not department_id:
            # Something went wrong – restart
            session.stage = "library_menu"
            session.save()
            send_library_menu(phone_number_id, from_number)
            return HttpResponse("Missing department", status=200)

        _send_past_papers(phone_number_id, from_number, department_id, year_filter)
        session.stage = "library_menu"
        session.save()
        send_library_menu(phone_number_id, from_number)
        return HttpResponse("Past papers sent", status=200)

    # ------------------------------------------------------------------
    # Default fallback inside library flow
    # ------------------------------------------------------------------
    return HttpResponse("Library flow ignored", status=200)

# ---------------------------------------------------------------------------
# Helper sub‑functions
# ---------------------------------------------------------------------------

def _send_borrowed_books(phone_number_id: str, from_number: str, session: ChatSession) -> HttpResponse:
    try:
        student = Student.objects.get(reg_number=session.reg_number)
    except Student.DoesNotExist:
        send_whatsapp_message(phone_number_id, from_number, "❌ You need to log in first.")
        return HttpResponse("Not logged in", status=200)

    borrowed = Book.objects.filter(rendered_to=student, status="Rendered")
    if borrowed.exists():
        parts = []
        for book in borrowed:
            due = book.render_to.strftime("%Y-%m-%d") if book.render_to else "N/A"
            parts.append(
                f"*📘 {book.title}*\n"
                f"👤 Author: {book.author.name if book.author else 'N/A'}\n"
                f"🏷 ISBN: {book.isbn}\n"
                f"🗓 Due: {due}\n"
            )
        msg = "📚 *Your Borrowed Books:*\n\n" + "\n".join(parts)
    else:
        msg = "📭 You currently have no borrowed books."
    send_whatsapp_message(phone_number_id, from_number, msg)
    return HttpResponse("Borrowed books sent", status=200)


def _perform_book_search(phone_number_id: str, from_number: str, query: str) -> None:
    books = Book.objects.filter(
        Q(title__icontains=query)
        | Q(author__name__icontains=query)
        | Q(isbn__icontains=query)
        | Q(department__name__icontains=query)
    )
    if books.exists():
        lines = []
        for book in books[:5]:
            status = "✅ Available" if book.status == "Available" else "❌ Rendered"
            lines.append(
                f"*📘 {book.title}*\n"
                f"👤 Author: {book.author.name if book.author else 'N/A'}\n"
                f"🏷 ISBN: {book.isbn}\n"
                f"🏫 Department: {book.department.name if book.department else 'N/A'}\n"
                f"🔖 Status: {status}\n"
                f"🗂 Shelf: {book.shelf_location or 'N/A'}\n"
            )
        msg = "📚 *Search Results:*\n\n" + "\n".join(lines)
    else:
        msg = (
            "⚠️ No books found with that keyword.\n\n"
            "Try another keyword or type:\n"
            "• `library_my_borrowed`\n"
            "• `library_back_to_main`\n"
            "• `library_menu`"
        )
    send_whatsapp_message(phone_number_id, from_number, msg)


def _send_past_papers(phone_number_id: str, from_number: str, dept_id: int, year: int | None) -> None:
    filters: Dict[str, Any] = {"department_id": dept_id}
    if year:
        filters["academic_year"] = year

    past_papers = PastPaper.objects.filter(**filters)
    if not past_papers.exists():
        send_whatsapp_message(phone_number_id, from_number, "📭 No past papers found for that selection.")
        return

    for paper in past_papers[:5]:
        send_whatsapp_message(
            phone_number_id,
            from_number,
            f"*📝 {paper.title}*\n"
            f"📘 Academic Year: {paper.get_academic_year_display()}\n"
            f"📅 Published: {paper.published_year}\n"
            f"🏫 Department: {paper.department.name}\n"
            f"📎 Download:https://django-material-dash2-latest-4635.onrender.com{paper.pdf.url}",
        )
