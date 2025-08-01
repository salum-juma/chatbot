from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
from apps.pages.models import ChatSession,Inquiry,Guideline
from apps.pages.whatsapp.handlers.announcement_handler import handle_announcement_menu, handle_announcement_selection
from apps.pages.whatsapp.handlers.cafteria_handler import handle_cafeteria_flow
from apps.pages.whatsapp.handlers.language_handler import handle_language_selection
from apps.pages.whatsapp.handlers.english_handler import handle_english_flow
from apps.pages.whatsapp.handlers.swahili_handler import handle_swahili_flow
from apps.pages.whatsapp.handlers.library_handler import handle_library_flow
from apps.pages.whatsapp.handlers.login_handler import handle_login_flow
from apps.pages.whatsapp.utils.whatsapp import send_whatsapp_message

def handle_student_inquiries(phone_number_id, from_number):
    """Fetch FAQs from DB and send to student via WhatsApp"""
    inquiries = Inquiry.objects.all().order_by('-created_at')[:10]  # Limit to 10 latest

    if not inquiries.exists():
        send_whatsapp_message(phone_number_id, from_number, "❓ No FAQs available at the moment.")
        return HttpResponse("No inquiries", status=200)

    # Build formatted WhatsApp message
    msg = "*❓ Frequently Asked Questions:*\n\n"
    for idx, inquiry in enumerate(inquiries, 1):
        msg += f"*{idx}. {inquiry.question}*\n{inquiry.answer}\n\n"

    # Optional: Add note if more exist
    total_count = Inquiry.objects.count()
    if total_count > 10:
        msg += f"_And {total_count - 10} more..._\n"

    send_whatsapp_message(phone_number_id, from_number, msg.strip())
    return HttpResponse("Sent inquiries", status=200)

@csrf_exempt
def whatsapp_webhook(request):
    if request.method == 'GET':
        verify_token = 'developernkya'
        if request.GET.get('hub.verify_token') == verify_token:
            return HttpResponse(request.GET.get('hub.challenge'))
        return HttpResponse("Invalid verification token", status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            entry = data.get("entry", [])[0]
            changes = entry.get("changes", [])[0]
            value = changes.get("value", {})
            messages = value.get("messages", [])

            if not messages:
                return HttpResponse("No messages", status=200)

            message = messages[0]
            message_id = message.get("id")
            from_number = message.get("from")
            phone_number_id = value.get("metadata", {}).get("phone_number_id")

            # Extract text or interactive input
            interactive = message.get("interactive", {})
            if "button_reply" in interactive:
                text = interactive["button_reply"].get("id", "").lower()
            elif "list_reply" in interactive:
                text = interactive["list_reply"].get("id", "").lower()
            else:
                text = message.get("text", {}).get("body", "").lower()

            # Get or create session
            session, _ = ChatSession.objects.get_or_create(phone_number=from_number)

            # Avoid duplicate processing
            if session.last_message_id == message_id:
                return HttpResponse("Duplicate message ignored", status=200)
            session.last_message_id = message_id
            session.save()

            # --- Greeting / Start ---
            if text in ['hi', 'hello', 'start', 'hey']:
                return handle_language_selection(phone_number_id, from_number)

            # --- Language Selection ---
            if text.startswith("lang_english") or text in [
                'prospectives', 'suggestion_box', 'about_us',
                'our_programs', 'online_applications', 'our_contacts'
            ]:
                return handle_english_flow(text, phone_number_id, from_number)

            if text.startswith("lang_swahili"):
                return handle_swahili_flow(text, phone_number_id, from_number)

            # --- Student Login Entry Point ---
            if text == 'current_student':
                session.stage = 'awaiting_reg_number'
                session.reg_number = None
                session.save()
                send_whatsapp_message(
                    phone_number_id, from_number,
                    "👋 Welcome to AskJo! Please enter your registration number."
                )
                return HttpResponse("Awaiting reg number", status=200)

            # --- Delegate Login Handling ---
            if session.stage and session.stage.startswith('awaiting_'):
                return handle_login_flow(text, phone_number_id, from_number, session)

            # --- Cafeteria flow stage update fix ---
            if text == "student_cafeteria" and session.stage == 'student_portal_main':
                session.stage = 'cafeteria_selecting_item'
                session.save()
                response = handle_cafeteria_flow(text, phone_number_id, from_number, session)
                if response:
                    return response
            elif session.stage and session.stage.startswith("cafeteria_"):
                response = handle_cafeteria_flow(text, phone_number_id, from_number, session)
                if response:
                    return response

            # --- Student portal main menu ---
            if session.stage == 'student_portal_main':
                if text == "student_announcements":
                    return handle_announcement_menu(phone_number_id, from_number)

                elif text.startswith("ann_category_") or text == "ann_view_all":
                    return handle_announcement_selection(text, phone_number_id, from_number)

                if text == "student_library":
                    session.stage = "library_menu"
                    session.save()
                    return handle_library_flow(text, phone_number_id, from_number, session)

                if text == "student_inquiries":
                    # send_whatsapp_message(phone_number_id, from_number, "❓ FAQ and common questions.")
                    # return HttpResponse("Sent inquiries", status=200)
                    return handle_student_inquiries(phone_number_id, from_number)

                if text == "student_guidelines":
                    guidelines = Guideline.objects.all()

                    if guidelines.exists():
                        msg = "*📖 University Guidelines:*\n\n"
                        for guide in guidelines:
                            msg += f"🔹 *{guide.title}*\n{guide.name}\n\n"

                        send_whatsapp_message(phone_number_id, from_number, msg.strip())
                    else:
                        send_whatsapp_message(phone_number_id, from_number, "📭 No guidelines have been published yet.")

                    return HttpResponse("Sent guidelines", status=200)


                if text == "back_to_main_menu":
                    send_whatsapp_message(phone_number_id, from_number, "🔙 Back to the main menu.")
                    return HttpResponse("Returned to main menu", status=200)

            # --- Delegate to Library Handler ---
            if session.stage in [
                'library_menu',
                'library_search',
                'past_paper_choose_department',
                'past_paper_choose_year'
            ] or text == 'student_library':
                return handle_library_flow(text, phone_number_id, from_number, session)

            # --- Fallback ---
            send_whatsapp_message(phone_number_id, from_number, "🤖 Unrecognized input. Type *hello* to start.")
            return HttpResponse("Unknown input", status=200)

        except Exception as e:
            print("Webhook error:", str(e))
            return HttpResponse("Error", status=500)

    return HttpResponse("Invalid request", status=400)


def handle_student_inquiries(phone_number_id, from_number):
    """Fetch FAQs from DB and send to student via WhatsApp"""
    inquiries = Inquiry.objects.all().order_by('-created_at')[:10]  # Limit to 10 latest

    if not inquiries.exists():
        send_whatsapp_message(phone_number_id, from_number, "❓ No FAQs available at the moment.")
        return HttpResponse("No inquiries", status=200)

    # Build formatted WhatsApp message
    msg = "*❓ Frequently Asked Questions:*\n\n"
    for idx, inquiry in enumerate(inquiries, 1):
        msg += f"*{idx}. {inquiry.question}*\n{inquiry.answer}\n\n"

    # Optional: Add note if more exist
    total_count = Inquiry.objects.count()
    if total_count > 10:
        msg += f"_And {total_count - 10} more..._\n"

    send_whatsapp_message(phone_number_id, from_number, msg.strip())
    return HttpResponse("Sent inquiries", status=200)