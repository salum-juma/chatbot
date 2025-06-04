from ..utils.whatsapp import (
    send_whatsapp_message,
    send_group_selection_list
)
from django.http import HttpResponse

def handle_english_flow(text, phone_number_id, from_number):
    if text == "lang_english":
        send_group_selection_list(phone_number_id, from_number)
    elif text == "prospectives":
        send_whatsapp_message(phone_number_id, from_number, "You selected *Prospectives*. Here's what you need to know about admissions and programs.")
    elif text == "current_student":
        send_whatsapp_message(phone_number_id, from_number, "Welcome *Current Student*! Access services, support, and announcements.")
    elif text == "suggestion_box":
        send_whatsapp_message(phone_number_id, from_number, "You selected the *Suggestion Box*. Feel free to share your ideas or concerns.")
    else:
        send_whatsapp_message(phone_number_id, from_number, "Unknown option in English flow.")
    return HttpResponse("English flow processed", status=200)
