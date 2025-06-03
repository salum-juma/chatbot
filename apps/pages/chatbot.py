from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import JsonResponse
import json

@csrf_exempt
def whatsapp_webhook(request):
    if request.method == 'GET':
        # Meta webhook verification
        verify_token = 'developernkya'
        if request.GET.get('hub.verify_token') == verify_token:
            return HttpResponse(request.GET.get('hub.challenge'))
        return HttpResponse("Invalid verification token", status=403)

    elif request.method == 'POST':
        # Here you handle incoming messages
        # This will be covered in the next step
        return HttpResponse("Message received")

    return HttpResponse("Invalid request", status=400)


def chatbot_response(message):
    if 'hello' in message.lower():
        return "Hi! How can I assist you today?"
    elif 'book' in message.lower():
        return "Do you want to check book availability or borrow one?"
    else:
        return "Sorry, I didn’t understand that. Can you rephrase?"

