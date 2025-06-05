from django.db.models import Q
from apps.pages.models import Book, ChatSession
from apps.pages.whatsapp.utils.whatsapp import send_whatsapp_message
from django.http import HttpResponse

def handle_library_flow(text, phone_number_id, from_number, session):
    # 1. First entry into library
    if text == "student_library":
        session.stage = "library_search"
        session.save()
        send_whatsapp_message(
            phone_number_id,
            from_number,
            "📚 *Welcome To SJUT Library Management System!*\n\nTo search for a book, just type its *title*, *author*, *ISBN*, or *department* below."
        )
        return HttpResponse("Library welcome sent", status=200)

    # 2. User is searching a book
    elif session.stage == "library_search":
        search_query = text.strip()

        # Search across title, author name, ISBN, and department
        books = Book.objects.filter(
            Q(title__icontains=search_query) |
            Q(author__name__icontains=search_query) |
            Q(isbn__icontains=search_query) |
            Q(department__name__icontains=search_query)
        )

        if books.exists():
            results = []
            for book in books[:5]:  # Show only top 5 results
                shelf = book.shelf_location  # uses @property
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
                "⚠️ No books found with that keyword. Try something else like 'biology', 'Shakespeare', or an ISBN."
            )

        return HttpResponse("Library search completed", status=200)

    return HttpResponse("Library flow ignored", status=200)


def handle_library_flow(text, phone_number_id, from_number, session):
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

        elif text == "library_my_borrowed":
            student = Student.objects.filter(phone_number=from_number).first()
            if not student:
                send_whatsapp_message(phone_number_id, from_number, "❌ You are not registered as a student.")
                return HttpResponse("Student not found", status=200)

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
            # You can reuse your student portal main menu function or just send a list here
            # For brevity, a simple message:
            send_whatsapp_message(phone_number_id, from_number, "🔙 Returning to the main menu.")
            return HttpResponse("Returned to main menu", status=200)

        else:
            send_whatsapp_message(phone_number_id, from_number, "⚠️ Invalid option. Please select from the list.")
            send_library_menu(phone_number_id, from_number)
            return HttpResponse("Invalid library option", status=200)

    elif session.stage == "library_search":
        search_query = text.strip()

        # Search across title, author name, ISBN, and department
        books = Book.objects.filter(
            Q(title__icontains=search_query) |
            Q(author__name__icontains=search_query) |
            Q(isbn__icontains=search_query) |
            Q(department__name__icontains=search_query)
        )

        if books.exists():
            results = []
            for book in books[:5]:  # Show only top 5 results
                shelf = book.shelf_location  # uses @property
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
                "⚠️ No books found with that keyword. Try something else like 'biology', 'Shakespeare', or an ISBN."
            )

        return HttpResponse("Library search completed", status=200)

    # Other existing library flow code...

    return HttpResponse("Library flow ignored", status=200)




def send_library_menu(phone_number_id, to):
    sections = [{
        "title": "📚 Library Menu",
        "rows": [
            {"id": "library_search_books", "title": "🔍 Search Book", "description": "Search books by title, author, ISBN, or department."},
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

