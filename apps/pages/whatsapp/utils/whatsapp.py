import requests

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