import requests

access_token = "EAAZACvoUcqEgBPdgUkpOqYwi5kGUk1pBWDIBJerUbyeF6QqbzKr3wAwNPn9BoYCfacLR2hQX8QBjBWTJtoEvPvUEnbXKxPRgQ4mSF39ecA3hShtlpwbv5BAwo0ctLkBt1l5jciIa3ND84cqDgi9ZBctQ4nZCRH6IjypstAcanRXPX1rsHrZAaThGMbOAWVv9ddeZB8uKu9aboH7rTZCD0ZAqUj3W14c7J3x4qObF6ALL"


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
                "text": "Hello! 👋 Welcome to AskJo, your smart assistant for St. Joseph University in Tanzania.\n\nPlease click proceed to continue."
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "lang_english",
                            "title": "Proceed"
                        }
                    }
                    # {
                    #     "type": "reply",
                    #     "reply": {
                    #         "id": "lang_swahili",
                    #         "title": "🇹🇿 Swahili"
                    #     }
                    # }
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


def send_announcement_category(phone_number_id, to, body, sections, button="View Options"):
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
                "text": "📢 Announcements"
            },
            "body": {
                "text": body
            },
            "footer": {
                "text": "Choose a category below 👇"
            },
            "action": {
                "button": button,
                "sections": sections
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    print("List message response:", response.status_code, response.text)
    return response.json()
