from django.contrib.auth import authenticate
from apps.pages.whatsapp.utils.whatsapp import send_whatsapp_message, send_whatsapp_list_message
from django.http import HttpResponse
from apps.pages.whatsapp.utils.eng_menu import send_student_services_menu
from apps.pages.models import Student


def normalize_phone_number(phone_number: str):
    """
    Convert local or WhatsApp number to +255XXXXXXXXX format.
    """
    if not phone_number:
        return None

    # Remove spaces and leading +
    phone_number = phone_number.replace(" ", "").replace("+", "")

    # Convert starting with 0 to 255 (Tanzania)
    if phone_number.startswith("0"):
        phone_number = "255" + phone_number[1:]

    # Ensure it starts with +
    return f"+{phone_number}"

def handle_login_flow(text, phone_number_id, from_number, session):
    if session.stage == 'awaiting_reg_number':
        session.reg_number = text
        session.stage = 'awaiting_password'
        session.save()
        send_whatsapp_message(
            phone_number_id, from_number,
            "🔐 Enter your Vcampus password to confirm your identity."
        )
        return HttpResponse("Awaiting password", status=200)

    if session.stage == 'awaiting_password':
        user = authenticate(username=session.reg_number, password=text)
        if user:
            session.stage = 'student_portal_main'

              # Default to not first year
            session.data['first_year'] = False

            # Only check student details if role is student
            if user.role == 'student':
                from_number_normalized = normalize_phone_number(from_number)

                student = Student.objects.filter(user=user).first()
                if student and student.phone_number:
                    student_phone_normalized = normalize_phone_number(student.phone_number)

                    # ✅ Match normalized numbers
                    if student_phone_normalized == from_number_normalized:
                        # Check if student is first year
                        if student.year and student.year.number == 1:
                            session.data['first_year'] = True

            session.save()
            send_student_services_menu(phone_number_id, from_number)
            return HttpResponse("Login success", status=200)
        else:
            session.stage = 'awaiting_password_retry'
            session.save()
            send_whatsapp_message(
                phone_number_id, from_number,
                (
                    "❌ Invalid login.\n"
                    "Type *retry* to try again, *start over* to restart, or visit the link below if you forgot your password:\n\n"
                    "🔑 Forgot Password: https://django-material-dash2-latest-4635.onrender.com/forgot-password/"
                )
            )

            return HttpResponse("Invalid login", status=200)

    if session.stage == 'awaiting_password_retry':
        if text == 'retry':
            session.stage = 'awaiting_password'
            session.save()
            send_whatsapp_message(phone_number_id, from_number, "🔁 Please enter your password again.")
            return HttpResponse("Retrying login", status=200)

        elif text == 'start over':
            session.stage = 'awaiting_reg_number'
            session.reg_number = None
            session.save()
            send_whatsapp_message(phone_number_id, from_number, "🔁 Please enter your registration number again.")
            return HttpResponse("Restarting login", status=200)

        else:
            send_whatsapp_message(phone_number_id, from_number,
                (
                    "❌ Invalid login.\n"
                    "Type *retry* to try again, *start over* to restart, or reset your password here:\n\n"
                    "🔑 Forgot Password: https://django-material-dash2-latest-4635.onrender.com/forgot-password/"
                )
            )
            return HttpResponse("Invalid retry input", status=400)

