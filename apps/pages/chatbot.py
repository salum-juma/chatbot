from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
from django.contrib.auth import authenticate
from apps.pages.models import ChatSession
from apps.pages.whatsapp.handlers.language_handler import handle_language_selection
from apps.pages.whatsapp.handlers.english_handler import handle_english_flow
from apps.pages.whatsapp.handlers.swahili_handler import handle_swahili_flow
from apps.pages.whatsapp.utils.whatsapp import send_whatsapp_message, send_whatsapp_list_message

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
                return HttpResponse("No messages to process", status=200)

            message = messages[0]
            from_number = message.get("from")
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

            # Start flow
            if text in ['hi', 'hello', 'start', 'hey']:
                return handle_language_selection(phone_number_id, from_number)

            elif text.startswith("lang_english") or text in ['prospectives', 'suggestion_box']:
                return handle_english_flow(text, phone_number_id, from_number)

            elif text.startswith("lang_swahili"):
                return handle_swahili_flow(text, phone_number_id, from_number)

            elif text == 'current_student':
                session.stage = 'awaiting_reg_number'
                session.save()
                send_whatsapp_message(
                    phone_number_id,
                    from_number,
                    "Hello! 👋 Welcome to AskJo, your smart assistant for St. Joseph University.\n\nPlease enter your registration number to continue."
                )
                return HttpResponse("Awaiting registration number", status=200)

            elif session.stage == 'awaiting_reg_number':
                session.reg_number = text
                session.stage = 'awaiting_password'
                session.save()
                send_whatsapp_message(
                    phone_number_id,
                    from_number,
                    "Please enter your Vcampus password to confirm your identity.\n\n(Tafadhali weka nenosiri lako la Vcampus ili kuthibitisha utambulisho wako)"
                )
                return HttpResponse("Awaiting password", status=200)

            elif session.stage == 'awaiting_password':
                user = authenticate(username=session.reg_number, password=text)
                if user is not None:
                    session.stage = 'student_portal_main'
                    session.save()

                    # Prepare list message with descriptions
                    sections = [
                        {
                            "title": "📚 Student Services",
                            "rows": [
                                {
                                    "id": "student_announcements",
                                    "title": "📢 Announcements",
                                    "description": "Be updated on current news/events."
                                },
                                {
                                    "id": "student_library",
                                    "title": "📚 Library Management",
                                    "description": "Search and find books easily."
                                },
                                {
                                    "id": "student_inquiries",
                                    "title": "❓ Student Inquiries",
                                    "description": "View answers to common questions."
                                },
                                {
                                    "id": "student_guidelines",
                                    "title": "📖 Guidelines",
                                    "description": "Steps for various university processes."
                                },
                                {
                                    "id": "student_cafeteria",
                                    "title": "🍽️ Cafeteria",
                                    "description": "Order from the university restaurant."
                                },
                                {
                                    "id": "back_to_main_menu",
                                    "title": "🔙 Rudi Menyu Kuu",
                                    "description": "Return to the main menu."
                                }
                            ]
                        }
                    ]

                    send_whatsapp_list_message(
                        phone_number_id,
                        from_number,
                        body="🎓 *Welcome to Student Portal!*\n\nPlease select a service to continue:",
                        sections=sections
                    )
                    return HttpResponse("Student portal options sent", status=200)

                else:
                    session.stage = 'awaiting_password_retry'
                    session.save()
                    send_whatsapp_message(
                        phone_number_id,
                        from_number,
                        "❌ Invalid credentials.\n\nPlease choose:\n"
                        "1️⃣ Type *retry* to enter your password again\n"
                        "2️⃣ Type *start over* to enter a new registration number"
                    )
                    return HttpResponse("Invalid credentials", status=401)

            elif session.stage == 'awaiting_password_retry':
                if text == 'retry':
                    session.stage = 'awaiting_password'
                    session.save()
                    send_whatsapp_message(
                        phone_number_id,
                        from_number,
                        "Please enter your Vcampus password again."
                    )
                    return HttpResponse("Retrying password", status=200)

                elif text == 'start over':
                    session.stage = 'awaiting_reg_number'
                    session.reg_number = None
                    session.save()
                    send_whatsapp_message(
                        phone_number_id,
                        from_number,
                        "🔄 Let's start over. Please enter your registration number again."
                    )
                    return HttpResponse("Restarting registration", status=200)

                else:
                    send_whatsapp_message(
                        phone_number_id,
                        from_number,
                        "❗ Invalid choice.\nType *retry* to enter your password again or *start over* to use a new registration number."
                    )
                    return HttpResponse("Invalid choice", status=200)

            elif session.stage == 'student_portal_main':
                # Respond to list reply selections
                if text == "student_announcements":
                    send_whatsapp_message(phone_number_id, from_number, "📢 Here are the latest announcements...")
                elif text == "student_library":
                    send_whatsapp_message(phone_number_id, from_number, "📚 Library services will be available soon.")
                elif text == "student_inquiries":
                    send_whatsapp_message(phone_number_id, from_number, "❓ FAQ and common student questions go here.")
                elif text == "student_guidelines":
                    send_whatsapp_message(phone_number_id, from_number, "📖 Guidelines for university processes.")
                elif text == "student_cafeteria":
                    send_whatsapp_message(phone_number_id, from_number, "🍽️ View and order from the cafeteria menu.")
                elif text == "back_to_main_menu":
                    session.stage = 'student_portal_main'
                    session.save()
                    send_whatsapp_message(phone_number_id, from_number, "🔙 You're now at the main menu.")
                else:
                    send_whatsapp_message(phone_number_id, from_number, "❓ Unknown command. Please select from the list.")
                    return HttpResponse("Unknown student_portal_main command", status=200)

            else:
                send_whatsapp_message(phone_number_id, from_number, "🤖 Sorry, I didn’t understand that. Please type *hello* to begin or *cancel* to exit.")
                return HttpResponse("Unknown command", status=200)

        except Exception as e:
            print("Webhook error:", str(e))
            return HttpResponse("Error", status=500)

    return HttpResponse("Invalid request", status=400)
