import requests

access_token = "EAAOvQZB8KEQ4BO4ZCwaIMwZBLeNH80Hg78hUsvZA0v2plcZChO6Eqpwekn3QRGdB0s3rgBjaSK6XlwCwCHA2LZCrfYlcALhsjoJsJepfiIFNj4u2LOeAM5plXQGPm8e4UbWFSqRGhZBG3vgdE0NuR8kZBjiPGPOwKym1QY7gePWri5WqaZAS5aEByTYff0NCLB1tZCqPZApran6QdIQVBAE6duRkUNW8louOrPDJnqtY0PE"


def send_group_selection_list(phone_number_id, to):
    url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
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


def send_language_selection(phone_number_id, to):
    url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
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



def send_whatsapp_message(phone_number_id, to, message):
    url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
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


def send_whatsapp_button_message(phone_number_id, to, body, buttons):
    url = f"https://graph.facebook.com/v17.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body},
            "action": {
                "buttons": buttons
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    print("Button message sent:", response.text)


def send_whatsapp_list_message(phone_number_id, to, body, sections):
    url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {
                "type": "text",
                "text": "🎓 Student Portal"
            },
            "body": {
                "text": body
            },
            "footer": {
                "text": "Choose one option below 👇"
            },
            "action": {
                "button": "View Services",
                "sections": sections
            }
        }
    }

    requests.post(url, headers=headers, json=payload)
    


def send_whatsapp_prospectives_menu(phone_number_id, to):
    url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {
                "type": "text",
                "text": "Prospectives Menu"
            },
            "body": {
                "text": "You selected *Prospectives*. Here's what you need to know about admissions and programs. Please select an option:"
            },
            "footer": {
                "text": "AskJo - St. Joseph University"
            },
            "action": {
                "button": "Select Option",
                "sections": [
                    {
                        "title": "Prospectives Options",
                        "rows": [
                            {
                                "id": "about_us",
                                "title": "About Us",
                                "description": "Learn more about St. Joseph University"
                            },
                            {
                                "id": "our_programs",
                                "title": "Our Programs",
                                "description": "Available at our campus"
                            },
                            {
                                "id": "online_applications",
                                "title": "Online Applications",
                                "description": "Register for our various online programs"
                            },
                            {
                                "id": "our_contacts",
                                "title": "Our Contacts",
                                "description": "Get more information and live support"
                            }
                        ]
                    }
                ]
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    print("Prospectives menu response:", response.status_code, response.json())
    return response.json()
