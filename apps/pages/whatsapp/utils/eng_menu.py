
from apps.pages.whatsapp.utils.whatsapp import send_whatsapp_list_message

def send_student_services_menu(phone_number_id, to):
    sections = [{
        "title": "📚 Student Services",
        "rows": [
            {"id": "student_announcements", "title": "📢 Announcements", "description": "Be updated on current news/events."},
            {"id": "student_library", "title": "📚 Library Management", "description": "Search and find books easily."},
            {"id": "student_inquiries", "title": "❓ Student Inquiries", "description": "View answers to common questions."},
            {"id": "student_guidelines", "title": "📖 Guidelines", "description": "Steps for various university processes."},
            {"id": "student_cafeteria", "title": "🍽️ Cafeteria", "description": "Order from the university restaurant."},
            {"id": "back_to_main_menu", "title": "🔙 Rudi Menyu Kuu", "description": "Return to the main menu."}
        ]
    }]

    send_whatsapp_list_message(
        phone_number_id, to,
        body="🎓 *Welcome to Student Portal!*\n\nPlease select a service to continue:",
        sections=sections
    )
