from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
from django.contrib.auth import authenticate
from apps.pages.models import ChatSession, Student, Book
from apps.pages.whatsapp.handlers.language_handler import handle_language_selection
from apps.pages.whatsapp.handlers.english_handler import handle_english_flow
from apps.pages.whatsapp.handlers.swahili_handler import handle_swahili_flow
from apps.pages.whatsapp.utils.whatsapp import send_whatsapp_message, send_whatsapp_list_message
from apps.pages.whatsapp.handlers.library_handler import handle_library_flow, send_library_menu


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

            session, _ = ChatSession.objects.get_or_create(phone_number=from_number)

            # Language selection entry point
            if text in ['hi', 'hello', 'start', 'hey']:
                return handle_language_selection(phone_number_id, from_number)

            # Language flows
            if text.startswith("lang_english") or text in ['prospectives', 'suggestion_box']:
                return handle_english_flow(text, phone_number_id, from_number)

            if text.startswith("lang_swahili"):
                return handle_swahili_flow(text, phone_number_id, from_number)

            # Student login
            if text == 'current_student':
                session.stage = 'awaiting_reg_number'
                session.save()
                send_whatsapp_message(
                    phone_number_id, from_number,
                    "👋 Welcome to AskJo! Please enter your registration number."
                )
                return HttpResponse("Awaiting reg number", status=200)

            if session.stage == 'awaiting_reg_number':
                session.reg_number = text
                session.stage = 'awaiting_password'
                session.save()
                send_whatsapp_message(
                    phone_number_id, from_number,
                    "🔐 Enter your Vcampus password to confirm your identity."
                )
                return HttpResponse("Awaiting password", status=200)

            if session.stage == 'awaiting_password':
                user = authenticate(username=session.reg_number, password=text)
                if user:
                    session.stage = 'student_portal_main'
                    session.save()

                    sections = [{
                        "title": "📚 Student Services",
                        "rows": [
                            {"id": "student_announcements", "title": "📢 Announcements", "description": "Be updated on current news/events."},
                            {"id": "student_library", "title": "📚 Library Management", "description": "Search and find books easily."},
                            {"id": "student_inquiries", "title": "❓ Student Inquiries", "description": "View answers to common questions."},
                            {"id": "student_guidelines", "title": "📖 Guidelines", "description": "Steps for various university processes."},
                            {"id": "student_cafeteria", "title": "🍽️ Cafeteria", "description": "Order from the university restaurant."},
                            {"id": "back_to_main_menu", "title": "🔙 Rudi Menyu Kuu", "description": "Return to the main menu."}
                        ]
                    }]

                    send_whatsapp_list_message(
                        phone_number_id, from_number,
                        body="🎓 *Welcome to Student Portal!*\n\nPlease select a service to continue:",
                        sections=sections
                    )
                    return HttpResponse("Options sent", status=200)
                else:
                    session.stage = 'awaiting_password_retry'
                    session.save()
                    send_whatsapp_message(
                        phone_number_id, from_number,
                        "❌ Invalid login.\nType *retry* to try again or *start over*."
                    )
                    return HttpResponse("Invalid login", status=401)

            if session.stage == 'awaiting_password_retry':
                if text == 'retry':
                    session.stage = 'awaiting_password'
                    session.save()
                    send_whatsapp_message(phone_number_id, from_number, "🔁 Please enter your password again.")
                    return HttpResponse("Retrying", status=200)
                elif text == 'start over':
                    session.stage = 'awaiting_reg_number'
                    session.reg_number = None
                    session.save()
                    send_whatsapp_message(phone_number_id, from_number, "🔁 Please enter your registration number again.")
                    return HttpResponse("Restarting", status=200)

            # Student Portal options
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

            # Delegate all library flows
            if session.stage in ['library_menu', 'library_search']:
                return handle_library_flow(text, phone_number_id, from_number, session)

            # Fallback
            send_whatsapp_message(phone_number_id, from_number, "🤖 Unrecognized input. Type *hello* to start.")
            return HttpResponse("Unknown input", status=200)

        except Exception as e:
            print("Webhook error:", str(e))
            return HttpResponse("Error", status=500)

    return HttpResponse("Invalid request", status=400)
