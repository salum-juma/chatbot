from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
import requests

@csrf_exempt
def whatsapp_webhook(request):
    if request.method == 'GET':
        verify_token = 'developernkya'
        if request.GET.get('hub.verify_token') == verify_token:
            return HttpResponse(request.GET.get('hub.challenge'))
        return HttpResponse("Invalid verification token", status=403)

    elif request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        entry = data.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        if messages:
            message = messages[0]
            text = message.get("text", {}).get("body", "").lower()
            from_number = message.get("from")
            phone_number_id = value.get("metadata", {}).get("phone_number_id")
            access_token = "EAAOvQZB8KEQ4BOxNL1opTcMuL7O83iQGzQif96K5RbZCNPeFMJho3eYeP1c7Xhc2F85RhbMRb68Nzs6G6ai4LBr3bFyLJHXBmvD7qLmBXZA046IEf73UeRmbrzZARbI7SXD3wZBXYMTOVeTIt1eAN1sgbg7LE1H4W8Ig0uppXSXATKZCZCrjxRzkKELTWu34utQKqXMsWIhZB6JgRW8VooUhPyH4lPoHiZBD8iZCkZD"

            # Check for greetings to send welcome message
            if text in ['hi', 'hello', 'start', 'hey']:
                reply = (
                    "Hello! 👋 Welcome to AskJo, your smart assistant for St. Joseph University in Tanzania.\n"
                    "How can I assist you today? Please select your preferred language:\n\n"
                    "🇬🇧 English\n"
                    "🇹🇿 Swahili\n\n"
                    "NB: You can type 'cancel' at any time to end the bot.\n\n"
                    "(Habari! 👋 Karibu AskJo, msaidizi wako wa kidijitali kwa Chuo Kikuu cha Mtakatifu Joseph Tanzania.\n"
                    "Nawezaje kukusaidia leo? Tafadhali chagua lugha unayopendelea:)"
                )
            else:
                reply = chatbot_response(text)

            send_whatsapp_message(phone_number_id, from_number, reply, access_token)

        return HttpResponse("Message processed", status=200)

    return HttpResponse("Invalid request", status=400)


def chatbot_response(message):
    if 'book' in message:
        return "Do you want to check book availability or borrow one?"
    elif 'cancel' in message:
        return "The session has been cancelled. You can type 'hello' to start again."
    elif message in ['english', 'swahili']:
        return f"You selected {message.capitalize()}. How can I assist you?"
    else:
        return "Sorry, I didn’t understand that. Please type 'hello' to begin or 'cancel' to exit."


def send_whatsapp_message(phone_number_id, to, message, token):
    url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {
            "body": message
        }
    }
    response = requests.post(url, headers=headers, json=data)
    print("WhatsApp API response:", response.status_code, response.json())  # Debug log
    return response.json()
