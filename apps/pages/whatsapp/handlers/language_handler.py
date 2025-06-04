from ..utils.whatsapp import send_language_selection
from django.http import HttpResponse

def handle_language_selection(phone_number_id, from_number):
    send_language_selection(phone_number_id, from_number)
    return HttpResponse("Language selection sent", status=200)
