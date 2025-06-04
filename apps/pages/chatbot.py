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

            # Handle both button replies and text
            text = ""
            interactive = message.get("interactive", {})
            button_reply = message.get("interactive", {}).get("button_reply", {})
            if button_reply:
                text = button_reply.get("id", "").lower()
            elif "list_reply" in interactive:
                text = interactive["list_reply"].get("id", "").lower()
            else:
                text = message.get("text", {}).get("body", "").lower()

            from_number = message.get("from")
            phone_number_id = value.get("metadata", {}).get("phone_number_id")
            access_token = "EAAOvQZB8KEQ4BOxaSsxWyfZBZCk07eYryj4MTpsxKraHwdmD7hHC8n9TpWbsu5s3k5Q9zUUvfZAG4pT4xH1ZCyZBzjb5YE5Ngczp0E6fOXm8LwRuzZCfoN42LgmwZCtXfxNlwxbXZAWlonKa2IKePHasTvzhNtUtZAU6K99yCWJKkRWqVDIymJ3xi96OKVo81sJmGCVqWVkAQL4YtHNTUJqUejZCdIjoUmdREWTyygZD"

            if text in ['hi', 'hello', 'start', 'hey']:
                send_language_selection(phone_number_id, from_number, access_token)
            elif text == "lang_english":
                send_group_selection_list(phone_number_id, from_number, access_token)

            elif text == "lang_swahili":
                send_whatsapp_message(phone_number_id, from_number, "Karibu! (Swahili responses coming soon)", access_token)

            elif text == "prospectives":
                send_whatsapp_message(phone_number_id, from_number, "You selected *Prospectives*. Here's what you need to know about admissions and programs.", access_token)

            elif text == "current_student":
                send_whatsapp_message(phone_number_id, from_number, "Welcome *Current Student*! You can now access services, support, and announcements.", access_token)

            elif text == "suggestion_box":
                send_whatsapp_message(phone_number_id, from_number, "You selected the *Suggestion Box*. Feel free to share your ideas or concerns.", access_token)

            else:
                reply = chatbot_response(text)
                send_whatsapp_message(phone_number_id, from_number, reply, access_token)

        return HttpResponse("Message processed", status=200)

    return HttpResponse("Invalid request", status=400)


def send_group_selection_list(phone_number_id, to, token):
    url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {
                "type": "text",
                "text": "Group Selection"
            },
            "body": {
                "text": "Great! To serve you better, please select the group you belong to:"
            },
            "footer": {
                "text": "AskJo - St. Joseph University"
            },
            "action": {
                "button": "Select Here",
                "sections": [
                    {
                        "title": "Choose One",
                        "rows": [
                            {
                                "id": "prospectives",
                                "title": "Prospectives",
                                "description": "Learn about our programs & admission process"
                            },
                            {
                                "id": "current_student",
                                "title": "Current Student",
                                "description": "Access our services, announcements & support"
                            },
                            {
                                "id": "suggestion_box",
                                "title": "Suggestion Box",
                                "description": "General inquiries or anonymous suggestions."
                            }
                        ]
                    }
                ]
            }
        }
    }

    response = requests.post(url, headers=headers, json=data)
    print("List message response:", response.status_code, response.json())
    return response.json()


def chatbot_response(message):
    if message in ['lang_english']:
        return "You selected 🇬🇧 English. How can I assist you?"
    elif message in ['lang_swahili']:
        return "Umechagua 🇹🇿 Kiswahili. Naweza kukusaidiaje?"
    elif 'book' in message:
        return "Do you want to check book availability or borrow one?"
    elif message == 'cancel':
        return "The session has been cancelled. You can type 'hello' to start again."
    else:
        return "Sorry, I didn’t understand that. Please type 'hello' to begin or 'cancel' to exit."


def send_language_selection(phone_number_id, to, token):
    url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": "Hello! 👋 Welcome to AskJo, your smart assistant for St. Joseph University in Tanzania.\n\nPlease select your preferred language:\n\n(Habari! 👋 Karibu AskJo, msaidizi wako wa kidijitali kwa Chuo Kikuu cha Mtakatifu Joseph Tanzania. Tafadhali chagua lugha unayopendelea:)"
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "lang_english",
                            "title": "🇬🇧 English"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "lang_swahili",
                            "title": "🇹🇿 Swahili"
                        }
                    }
                ]
            }
        }
    }

    response = requests.post(url, headers=headers, json=data)
    print("Button message response:", response.status_code, response.json())
    return response.json()


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
        "text": {"body": message}
    }

    response = requests.post(url, headers=headers, json=data)
    print("Text message response:", response.status_code, response.json())
    return response.json()
