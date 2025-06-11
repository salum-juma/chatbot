from django.db.models import Q
from django.http import HttpResponse
from apps.pages.models import Book, PastPaper, Department, Student
from apps.pages.whatsapp.utils.whatsapp import send_whatsapp_message, send_whatsapp_list_message


def handle_library_flow(text, phone_number_id, from_number, session):
    # Handle initial entry to library menu
    if text == "student_library":
        try:
            student = Student.objects.get(reg_number=session.reg_number)
        except Student.DoesNotExist:
            session.stage = "awaiting_login"
            session.save()
            send_whatsapp_message(
                phone_number_id,
                from_number,
                "🔐 Please log in first by sending: `REG1234 yourpassword`"
            )
            return HttpResponse("Login required", status=200)

        session.stage = "library_menu"
        session.save()
        send_library_menu(phone_number_id, from_number)
        return HttpResponse("Library menu sent", status=200)

    # Library menu options
    if session.stage == "library_menu":
        if text == "library_search_books":
            session.stage = "library_search"
            session.save()
            send_whatsapp_message(
                phone_number_id,
                from_number,
                "📚 Please type the book title, author, ISBN, or department to search."
            )
            return HttpResponse("Prompted book search", status=200)

        elif text == "library_search_papers":
            # Start past paper interactive flow
            session.stage = "past_paper_choose_department"
            session.data = {}  # Clear any previous data
            session.save()
            send_department_options(phone_number_id, from_number)
            return HttpResponse("Sent department options", status=200)

        elif text == "library_my_borrowed":
            # Fetch student
            try:
                student = Student.objects.get(reg_number=session.reg_number)
            except Student.DoesNotExist:
                send_whatsapp_message(phone_number_id, from_number, "❌ You need to log in first.")
                return HttpResponse("Not logged in", status=200)

            borrowed_books = Book.objects.filter(rendered_to=student, status='Rendered')

            if borrowed_books.exists():
                results = []
                for book in borrowed_books:
                    due_date = book.render_to.strftime("%Y-%m-%d") if book.render_to else "N/A"
                    results.append(
                        f"*📘 {book.title}*\n"
                        f"👤 Author: {book.author.name if book.author else 'N/A'}\n"
                        f"🏷 ISBN: {book.isbn}\n"
                        f"🗓 Due Date: {due_date}\n"
                    )
                message = "📚 *Your Borrowed Books:*\n\n" + "\n".join(results)
                send_whatsapp_message(phone_number_id, from_number, message)
            else:
                send_whatsapp_message(phone_number_id, from_number, "📭 You currently have no borrowed books.")

            return HttpResponse("Sent borrowed books", status=200)

        elif text == "library_back_to_main":
            session.stage = "student_portal_main"
            session.save()
            send_whatsapp_message(phone_number_id, from_number, "🔙 Returning to the main menu.")
            return HttpResponse("Returned to main menu", status=200)

        else:
            send_whatsapp_message(phone_number_id, from_number, "⚠️ Invalid option. Please select from the list.")
            send_library_menu(phone_number_id, from_number)
            return HttpResponse("Invalid library option", status=200)

    # Book search stage
    elif session.stage == "library_search":
        if text in ["library_my_borrowed", "library_back_to_main", "library_menu"]:
            session.stage = "library_menu"
            session.save()
            return handle_library_flow(text, phone_number_id, from_number, session)

        search_query = text.strip()

        books = Book.objects.filter(
            Q(title__icontains=search_query) |
            Q(author__name__icontains=search_query) |
            Q(isbn__icontains=search_query) |
            Q(department__name__icontains=search_query)
        )

        if books.exists():
            results = []
            for book in books[:5]:
                shelf = book.shelf_location
                status = "✅ Available" if book.status == "Available" else "❌ Rendered"
                results.append(
                    f"*📘 {book.title}*\n"
                    f"👤 Author: {book.author.name if book.author else 'N/A'}\n"
                    f"🏷 ISBN: {book.isbn}\n"
                    f"🏫 Department: {book.department.name if book.department else 'N/A'}\n"
                    f"🔖 Status: {status}\n"
                    f"🗂 Shelf: {shelf}\n"
                )

            message = "📚 *Search Results:*\n\n" + "\n".join(results)
            send_whatsapp_message(phone_number_id, from_number, message)
        else:
            send_whatsapp_message(
                phone_number_id,
                from_number,
                "⚠️ No books found with that keyword. Try something else like 'biology', 'Shakespeare', or an ISBN.\n\n"
                "You can also type:\n• `library_my_borrowed`\n• `library_back_to_main`\n• `library_menu`"
            )

        return HttpResponse("Library search completed", status=200)

    # Past paper department selection stage
    elif session.stage == "past_paper_choose_department":
        try:
            selected_department = Department.objects.get(name__iexact=text.strip())
        except Department.DoesNotExist:
            send_whatsapp_message(phone_number_id, from_number, "⚠️ Invalid department. Please select from the list.")
            send_department_options(phone_number_id, from_number)
            return HttpResponse("Invalid department", status=200)

        # Save department in session data
        session.data = session.data or {}
        session.data['past_paper_department_id'] = selected_department.id
        session.stage = "past_paper_choose_year"
        session.save()

        send_year_options(phone_number_id, from_number)
        return HttpResponse("Sent year options", status=200)

    # Past paper year selection stage
    elif session.stage == "past_paper_choose_year":
        if text.lower() == "all":
            year_filter = None
        else:
            try:
                year_filter = int(text)
                if year_filter not in [1, 2, 3, 4]:
                    raise ValueError
            except ValueError:
                send_whatsapp_message(phone_number_id, from_number, "⚠️ Please select a valid year (1-4) or 'All'.")
                send_year_options(phone_number_id, from_number)
                return HttpResponse("Invalid year", status=200)

        department_id = session.data.get('past_paper_department_id')
        if not department_id:
            send_whatsapp_message(phone_number_id, from_number, "⚠️ Something went wrong, please start over.")
            session.stage = "library_menu"
            session.save()
            send_library_menu(phone_number_id, from_number)
            return HttpResponse("Missing department", status=200)

        filters = {'department_id': department_id}
        if year_filter:
            filters['academic_year'] = year_filter

        past_papers = PastPaper.objects.filter(**filters)
        if past_papers.exists():
            for paper in past_papers[:5]:  # limit results to first 5
                send_whatsapp_message(
                    phone_number_id,
                    from_number,
                    f"*📝 {paper.title}*\n"
                    f"📘 Academic Year: {paper.get_academic_year_display()}\n"
                    f"📅 Published: {paper.published_year}\n"
                    f"🏫 Department: {paper.department.name}\n"
                    f"📎 Download: {paper.pdf.url}"
                )
        else:
            send_whatsapp_message(
                phone_number_id,
                from_number,
                "📭 No past papers found for that selection."
            )

        # Return user to library menu
        session.stage = "library_menu"
        session.save()
        send_library_menu(phone_number_id, from_number)
        return HttpResponse("Past papers sent", status=200)

    # Default fallback response
    return HttpResponse("Library flow ignored", status=200)


def send_library_menu(phone_number_id, to):
    sections = [{
        "title": "📚 Library Menu",
        "rows": [
            {"id": "library_search_books", "title": "🔍 Search Book", "description": "Search books by title, author, ISBN, or department."},
            {"id": "library_search_papers", "title": "📝 Search Past Papers", "description": "Find past exam papers by department and year."},
            {"id": "library_my_borrowed", "title": "📖 My Borrowed Books", "description": "View books you have currently borrowed."},
            {"id": "library_back_to_main", "title": "🔙 Back to Main Menu", "description": "Return to the main student menu."}
        ]
    }]

    send_whatsapp_list_message(
        phone_number_id,
        to,
        body="Welcome to the Library Management System. Please select an option:",
        sections=sections
    )


def send_department_options(phone_number_id, to):
    departments = Department.objects.all()
    sections = [{
        "title": "Departments",
        "rows": [{"id": dept.name, "title": dept.name} for dept in departments]
    }]
    send_whatsapp_list_message(
        phone_number_id,
        to,
        body="Please select the department:",
        sections=sections
    )


def send_year_options(phone_number_id, to):
    years = [
        {"id": "1", "title": "1st Year"},
        {"id": "2", "title": "2nd Year"},
        {"id": "3", "title": "3rd Year"},
        {"id": "4", "title": "4th Year"},
        {"id": "all", "title": "All Years"},
    ]
    sections = [{
        "title": "Academic Year",
        "rows": years
    }]
    send_whatsapp_list_message(
        phone_number_id,
        to,
        body="Please select the academic year:",
        sections=sections
    )
