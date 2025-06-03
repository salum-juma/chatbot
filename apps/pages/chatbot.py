from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@csrf_exempt
def whatsapp_webhook(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message')  # Depends on your provider's payload

        # Call your chatbot logic
        reply = chatbot_response(user_message)

        # Return response in WhatsApp-compatible format
        return JsonResponse({"reply": reply})
    return JsonResponse({"error": "Invalid method"}, status=400)


def chatbot_response(message):
    if 'hello' in message.lower():
        return "Hi! How can I assist you today?"
    elif 'book' in message.lower():
        return "Do you want to check book availability or borrow one?"
    else:
        return "Sorry, I didn’t understand that. Can you rephrase?"

