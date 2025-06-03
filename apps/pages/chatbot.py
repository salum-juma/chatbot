from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import JsonResponse
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
            text = message.get("text", {}).get("body", "")
            from_number = message.get("from")
            phone_number_id = value.get("metadata", {}).get("phone_number_id")
            access_token = "EAAOvQZB8KEQ4BOxNL1opTcMuL7O83iQGzQif96K5RbZCNPeFMJho3eYeP1c7Xhc2F85RhbMRb68Nzs6G6ai4LBr3bFyLJHXBmvD7qLmBXZA046IEf73UeRmbrzZARbI7SXD3wZBXYMTOVeTIt1eAN1sgbg7LE1H4W8Ig0uppXSXATKZCZCrjxRzkKELTWu34utQKqXMsWIhZB6JgRW8VooUhPyH4lPoHiZBD8iZCkZD"  # Replace with your real token

            reply = chatbot_response(text)
            send_whatsapp_message(phone_number_id, from_number, reply, access_token)

        return HttpResponse("Message processed", status=200)

    return HttpResponse("Invalid request", status=400)



def chatbot_response(message):
    if 'hello' in message.lower():
        return "Hi! How can I assist you today?"
    elif 'book' in message.lower():
        return "Do you want to check book availability or borrow one?"
    else:
        return "Sorry, I didn’t understand that. Can you rephrase?"
    


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
    return response.json()

