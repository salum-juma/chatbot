from django.http import HttpResponse
from apps.pages.whatsapp.utils.whatsapp import send_whatsapp_message
from apps.pages.models import Book

def handle_library_flow(text, phone_number_id, from_number, session):
    # Entry point to Library
    if text == "student_library":
        session.stage = "library_search"
        session.save()
        send_whatsapp_message(
            phone_number_id,
            from_number,
            "📚 *SJUT Library System*\n\n"
            "Type the *book name* you're looking for, and I’ll help you find its location in the library. 📖"
        )
        return HttpResponse("Library prompt sent", status=200)

    # Book search handler
    elif session.stage == "library_search":
        query = text.strip()
        results = Book.objects.filter(title__icontains=query)

        if results.exists():
            response_lines = [
                f"✅ *{book.title}* — 🗂 Shelf: {book.shelf_location}" for book in results
            ]
            response = "📖 *Search Results:*\n" + "\n".join(response_lines)
        else:
            response = (
                "❌ Sorry, no books found with that title.\n"
                "Try another title or type *back* to return to the main menu."
            )

        send_whatsapp_message(phone_number_id, from_number, response)
        return HttpResponse("Book search handled", status=200)

    return HttpResponse("Library fallback", status=200)
