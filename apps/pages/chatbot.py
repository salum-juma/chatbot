from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
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
        data = json.loads(request.body.decode('utf-8'))
        try:
            message = data["entry"][0]["changes"][0]["value"]["messages"][0]
            from_number = message["from"]
            phone_number_id = data["entry"][0]["changes"][0]["value"]["metadata"]["phone_number_id"]

            # Get the text or button reply
            text = ""
            interactive = message.get("interactive", {})
            button_reply = interactive.get("button_reply", {})
            if button_reply:
                text = button_reply.get("id", "").lower()
            elif "list_reply" in interactive:
                text = interactive["list_reply"].get("id", "").lower()
            else:
                text = message.get("text", {}).get("body", "").lower()

            # Delegate handling
            if text in ['hi', 'hello', 'start', 'hey']:
                return handle_language_selection(phone_number_id, from_number)

            elif text.startswith("lang_english") or text in ['prospectives', 'current_student', 'suggestion_box']:
                return handle_english_flow(text, phone_number_id, from_number)

            elif text.startswith("lang_swahili"):
                return handle_swahili_flow(text, phone_number_id, from_number)

            else:
                from apps.pages.whatsapp.utils.whatsapp import send_whatsapp_message
                reply = "Sorry, I didn’t understand that. Please type 'hello' to begin or 'cancel' to exit."
                send_whatsapp_message(phone_number_id, from_number, reply)
                return HttpResponse("Unknown command processed", status=200)

        except Exception as e:
            print("Webhook error:", str(e))
            return HttpResponse("Error", status=500)

    return HttpResponse("Invalid request", status=400)
