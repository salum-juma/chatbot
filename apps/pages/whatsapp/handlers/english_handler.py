from apps.pages.models import ChatSession
from ..utils.whatsapp import (
    send_whatsapp_message,
    send_group_selection_list,
    send_whatsapp_prospectives_menu,
)
from django.http import HttpResponse


def handle_english_flow(text, phone_number_id, from_number):
    if text == "lang_english":
        send_group_selection_list(phone_number_id, from_number)

    elif text == "prospectives":
        # Show the list of prospective options
        send_whatsapp_prospectives_menu(phone_number_id, from_number)

    elif text == "about_us":
        send_whatsapp_message(
            phone_number_id,
            from_number,
            "📘 *About Us* – St. Joseph University of Tanzania (SJUIT)\n\n"
            "St. Joseph University of Tanzania (SJUIT) is a leading institution with campuses in Mbezi-Luguruni and Boko, offering degrees and diplomas in Engineering, ICT, Science, Mathematics Education, Medicine, Pharmaceutical Sciences, and Nursing.\n\n"
            "SJUIT is a university preferred by students, parents, and employers for its employability. Our graduates are highly sought after for their knowledge, skills, discipline, and integrity.\n\n"
            "🔹 *Vision:* To be a leader in employability education in Africa and to be part of its history.\n"
            "🔹 *Mission:* To nurture the youth of Africa with quality, disciplined education, which ignites the light of self-awareness and national development.\n\n"
            "With a team of experienced professionals from Tanzania and abroad, we prepare young people to be tomorrow’s leaders with knowledge, ethics, and resilience.\n\n"
            "✨ *SJUIT: A Place Where Your Dreams Grow.*"
        )

    elif text == "our_programs":
        send_whatsapp_message(
            phone_number_id,
            from_number,
            "🎓 *Our Programs*\n\nWe offer a variety of undergraduate and postgraduate programs across different faculties. Explore what's available at our campus!"
        )

    elif text == "online_applications":
        send_whatsapp_message(
            phone_number_id,
            from_number,
             "📝 *Online Applications*\n\n"
             "Click the link below to apply for our programs online:\n\n"
             "🔗 http://sjuitadmission.com/admission-sjcet/onlineAdmission/login.php?type=DEGREE"
        )

    elif text == "our_contacts":
        send_whatsapp_message(
            phone_number_id,
            from_number,
            "📞 *Contact Us*\n\n"
            "📍 *Location:*\n"
            "St. Joseph University Tanzania\n"
            "P.O. Box 11007, Dar es Salaam, Tanzania\n\n"
            "✉ *Email:* info@sjuit.ac.tz\n\n"
            "📞 *Phone:*\n"
            "📌 College Office: +255 680 277 914\n"
            "📌 Admissions Office: +255 680 277 900 / +255 680 277 909 / +255 680 277 899 / +255 784 757 010"
        )

    elif text == "current_student":
        ChatSession.objects.update_or_create(
            phone_number=from_number,
            defaults={"state": "awaiting_registration"}
        )

        message = (
            "Hello! 👋 Welcome to AskJo, your smart assistant for St. Joseph University in Tanzania.\n\n"
            "Please enter your *registration number* to continue."
        )
        return send_whatsapp_message(phone_number_id, from_number, message)

    elif text == "suggestion_box":
        send_whatsapp_message(
            phone_number_id,
            from_number,
             "🗳 *Suggestion Box*\n\n"
             "Your feedback is important to us! \n"
             "Click the link below to submit your feedback anonymously:\n\n"
             "https://django-material-dash2-latest-dsh3.onrender.com/suggestions/"
        )

    else:
        send_whatsapp_message(phone_number_id, from_number, "Unknown option in English flow.")

    return HttpResponse("English flow processed", status=200)
