from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
from apps.pages.models import ChatSession
from apps.pages.whatsapp.handlers.language_handler import handle_language_selection
from apps.pages.whatsapp.handlers.english_handler import handle_english_flow
from apps.pages.whatsapp.handlers.swahili_handler import handle_swahili_flow
from apps.pages.whatsapp.handlers.library_handler import handle_library_flow, send_library_menu
from apps.pages.whatsapp.handlers.login_handler import handle_login_flow
from apps.pages.whatsapp.utils.whatsapp import send_whatsapp_message

@csrf_exempt
def whatsapp_webhook(request):
    if request.method == 'GET':
        verify_token = 'developernkya'
        if request.GET.get('hub.verify_token') == verify_token:
            return HttpResponse(request.GET.get('hub.challenge'))
        return HttpResponse("Invalid verification token", status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            entry = data.get("entry", [])[0]
            changes = entry.get("changes", [])[0]
            value = changes.get("value", {})
            messages = value.get("messages", [])

            if not messages:
                return HttpResponse("No messages", status=200)

            message = messages[0]
            from_number = message["from"]
            phone_number_id = value.get("metadata", {}).get("phone_number_id")

            interactive = message.get("interactive", {})
            text = ""

            if "button_reply" in interactive:
                text = interactive["button_reply"].get("id", "").lower()
            elif "list_reply" in interactive:
                text = interactive["list_reply"].get("id", "").lower()
            else:
                text = message.get("text", {}).get("body", "").lower()

            # Get or create chat session for this user
            session, _ = ChatSession.objects.get_or_create(phone_number=from_number)

            # Entry points
            if text in ['hi', 'hello', 'start', 'hey']:
                return handle_language_selection(phone_number_id, from_number)

            if text.startswith("lang_english") or text in ['prospectives', 'suggestion_box']:
                return handle_english_flow(text, phone_number_id, from_number)

            if text.startswith("lang_swahili"):
                return handle_swahili_flow(text, phone_number_id, from_number)

            if text == 'current_student':
                session.stage = 'awaiting_reg_number'
                session.reg_number = None
                session.save()
                send_whatsapp_message(
                    phone_number_id, from_number,
                    "👋 Welcome to AskJo! Please enter your registration number."
                )
                return HttpResponse("Awaiting reg number", status=200)

            # Login flow delegation
            if session.stage.startswith('awaiting_'):
                login_response = handle_login_flow(text, phone_number_id, from_number, session)
                if login_response:
                    return login_response

            # Student portal main menu options
            if session.stage == 'student_portal_main':
                if text == "student_announcements":
                    send_whatsapp_message(phone_number_id, from_number, "📢 Latest announcements coming soon...")
                    return HttpResponse("Sent announcements", status=200)

                if text == "student_library":
                    session.stage = "library_menu"
                    session.save()
                    send_library_menu(phone_number_id, from_number)
                    return HttpResponse("Library menu sent", status=200)

                if text == "student_inquiries":
                    send_whatsapp_message(phone_number_id, from_number, "❓ FAQ and common questions.")
                    return HttpResponse("Sent inquiries", status=200)

                if text == "student_guidelines":
                    send_whatsapp_message(phone_number_id, from_number, "📖 University processes guidelines.")
                    return HttpResponse("Sent guidelines", status=200)

                if text == "student_cafeteria":
                    send_whatsapp_message(phone_number_id, from_number, "🍽️ Order cafeteria meals here.")
                    return HttpResponse("Sent cafeteria", status=200)

                if text == "back_to_main_menu":
                    send_whatsapp_message(phone_number_id, from_number, "🔙 Back to the main menu.")
                    return HttpResponse("Returned to main menu", status=200)

            # Library flow delegation
            if session.stage in ['library_menu', 'library_search']:
                return handle_library_flow(text, phone_number_id, from_number, session)

            # Fallback
            send_whatsapp_message(phone_number_id, from_number, "🤖 Unrecognized input. Type *hello* to start.")
            return HttpResponse("Unknown input", status=200)

        except Exception as e:
            print("Webhook error:", str(e))
            return HttpResponse("Error", status=500)

    return HttpResponse("Invalid request", status=400)
