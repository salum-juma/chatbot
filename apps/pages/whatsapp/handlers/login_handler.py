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
    """
    Handle the student login flow including registration number, password, and first-year detection.
    """

    # --- Step 1: Awaiting registration number ---
    if session.stage == 'awaiting_reg_number':
        session.reg_number = text
        session.stage = 'awaiting_password'
        session.save()
        print(f"📝 Registration number received: {session.reg_number}")

        send_whatsapp_message(
            phone_number_id, from_number,
            "🔐 Enter your Vcampus password to confirm your identity."
        )
        return HttpResponse("Awaiting password", status=200)

    # --- Step 2: Awaiting password ---
    if session.stage == 'awaiting_password':
        print(f"🔍 Authenticating user: {session.reg_number}")
        user = authenticate(username=session.reg_number, password=text)

        if user:
            print("✅ Authentication successful")

            # Default stage after login
            session.stage = 'student_portal_main'
            session.data['first_year'] = False  # Default

            # --- Step 3: Check student and first-year status ---
            if user.role == 'student':
                from_number_normalized = normalize_phone_number(from_number)
                print(f"📞 Normalized from_number: {from_number} -> {from_number_normalized}")

                student = Student.objects.filter(user=user).first()
                if student:
                    student_phone_normalized = normalize_phone_number(student.phone_number)
                    print(f"👤 Student phone: {student.phone_number} -> {student_phone_normalized}")

                    if student_phone_normalized == from_number_normalized:
                        print("✅ Phone number match confirmed")
                        
                        # Check first-year status
                        if student.year and student.year.number == 1:
                            session.data['first_year'] = True
                            print("🎓 Student identified as FIRST YEAR")
                        else:
                            print("🎓 Student is NOT first year")
                    else:
                        print("⚠️ Phone number mismatch between DB and WhatsApp")
                else:
                    print("⚠️ No Student record linked to this user")

            # Save session with first_year info
            session.save()

            # Send student services menu
            send_student_services_menu(phone_number_id, from_number)
            return HttpResponse("Login success", status=200)

        else:
            print("❌ Authentication failed")
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

    # --- Step 3: Handle retry ---
    if session.stage == 'awaiting_password_retry':
        if text == 'retry':
            print("🔁 User requested password retry")
            session.stage = 'awaiting_password'
            session.save()
            send_whatsapp_message(phone_number_id, from_number, "🔁 Please enter your password again.")
            return HttpResponse("Retrying login", status=200)

        elif text == 'start over':
            print("🔄 User requested to start over")
            session.stage = 'awaiting_reg_number'
            session.reg_number = None
            session.save()
            send_whatsapp_message(phone_number_id, from_number, "🔁 Please enter your registration number again.")
            return HttpResponse("Restarting login", status=200)

        else:
            print(f"⚠️ Invalid retry input: {text}")
            send_whatsapp_message(phone_number_id, from_number,
                (
                    "❌ Invalid login.\n"
                    "Type *retry* to try again, *start over* to restart, or reset your password here:\n\n"
                    "🔑 Forgot Password: https://django-material-dash2-latest-4635.onrender.com/forgot-password/"
                )
            )
            return HttpResponse("Invalid retry input", status=400)
