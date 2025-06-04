from ..utils.whatsapp import send_whatsapp_message
from django.http import HttpResponse

def handle_swahili_flow(text, phone_number_id, from_number):
    if text == "lang_swahili":
        send_whatsapp_message(phone_number_id, from_number, "Karibu! (Majibu kwa Kiswahili yanakuja hivi karibuni.)")
    else:
        send_whatsapp_message(phone_number_id, from_number, "Chaguo halijatambulika kwa Kiswahili.")
    return HttpResponse("Swahili flow processed", status=200)
