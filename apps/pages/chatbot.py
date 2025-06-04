from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
from apps.pages.models import ChatSession
from apps.pages.whatsapp.handlers.language_handler import handle_language_selection
from apps.pages.whatsapp.handlers.english_handler import handle_english_flow
from apps.pages.whatsapp.handlers.swahili_handler import handle_swahili_flow


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
                print("No messages in webhook payload:", json.dumps(data, indent=2))
                return HttpResponse("No messages to process", status=200)

            message = messages[0]
            from_number = message.get("from")
            phone_number_id = value.get("metadata", {}).get("phone_number_id")

            # Retrieve or create chat session
            session, _ = ChatSession.objects.get_or_create(phone_number=from_number)

            # Extract text from message
            interactive = message.get("interactive", {})
            text = ""
            if "button_reply" in interactive:
                text = interactive["button_reply"].get("id", "").lower()
            elif "list_reply" in interactive:
                text = interactive["list_reply"].get("id", "").lower()
            else:
                text = message.get("text", {}).get("body", "").lower()

            # Delegate based on current session state
            if text in ['hi', 'hello', 'start', 'hey']:
                return handle_language_selection(phone_number_id, from_number)

            elif text.startswith("lang_english") or text in ['prospectives', 'suggestion_box']:
                return handle_english_flow(text, phone_number_id, from_number)
            
            elif text.startswith("lang_swahili"):
                return handle_swahili_flow(text, phone_number_id, from_number)

            elif text == 'current_student':
                session.stage = 'awaiting_reg_number'
                session.save()
                from apps.pages.whatsapp.utils.whatsapp import send_whatsapp_message
                msg = (
                    "Hello! 👋 Welcome to AskJo, your smart assistant for St. Joseph University in Tanzania. "
                    "Please enter your registration number to continue."
                )
                send_whatsapp_message(phone_number_id, from_number, msg)
                return HttpResponse("Awaiting registration number", status=200)

            elif session.stage == 'awaiting_reg_number':
                session.reg_number = text
                session.stage = 'awaiting_password'
                session.save()
                from apps.pages.whatsapp.utils.whatsapp import send_whatsapp_message
                msg = (
                    "Please enter your Vcampus password to confirm your identity.\n\n"
                    "(Tafadhali weka nenosiri lako la Vcampus ili kuthibitisha utambulisho wako)"
                )
                send_whatsapp_message(phone_number_id, from_number, msg)
                return HttpResponse("Awaiting password", status=200)

            elif session.stage == 'awaiting_password':
                session.password = text
                session.stage = 'authenticated'
                session.save()
                from apps.pages.whatsapp.utils.whatsapp import send_whatsapp_message
                send_whatsapp_message(phone_number_id, from_number, "✅ Logged in successfully.")
                return HttpResponse("Authenticated", status=200)

            else:
                from apps.pages.whatsapp.utils.whatsapp import send_whatsapp_message
                reply = "Sorry, I didn’t understand that. Please type 'hello' to begin or 'cancel' to exit."
                send_whatsapp_message(phone_number_id, from_number, reply)
                return HttpResponse("Unknown command processed", status=200)

        except Exception as e:
            print("Webhook error:", str(e))
            return HttpResponse("Error", status=500)

    return HttpResponse("Invalid request", status=400)
