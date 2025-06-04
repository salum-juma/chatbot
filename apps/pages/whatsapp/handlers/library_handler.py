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
