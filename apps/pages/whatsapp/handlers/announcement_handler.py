from apps.pages.models import Announcement, AnnouncementCategory
from apps.pages.whatsapp.utils.whatsapp import send_whatsapp_list_message, send_whatsapp_message
from django.http import HttpResponse
from collections import defaultdict

def handle_announcement_menu(phone_number_id, from_number):
    categories = AnnouncementCategory.objects.all()
    if not categories.exists():
        send_whatsapp_message(phone_number_id, from_number, "📭 No categories available.")
        return HttpResponse("No categories", status=200)

    sections = [{
        "title": "📚 Select Category to View",
        "rows": [
            {"id": f"ann_category_{cat.id}", "title": cat.name} for cat in categories
        ] + [{"id": "ann_view_all", "title": "📋 View All Announcements"}]
    }]

    send_whatsapp_list_message(
        phone_number_id, from_number,
        body="*📢 Announcements*\n\nTap a category below to view announcements:",
        sections=sections
    )
    return HttpResponse("Sent announcement menu", status=200)


def handle_announcement_selection(text, phone_number_id, from_number):
    if text == "ann_view_all":
        announcements = Announcement.objects.select_related('category').order_by('-created_at')
        return send_announcement_grouped(announcements, phone_number_id, from_number)

    elif text.startswith("ann_category_"):
        category_id = text.replace("ann_category_", "")
        announcements = Announcement.objects.filter(category_id=category_id).order_by('-created_at')
        return send_announcement_grouped(announcements, phone_number_id, from_number, single_category=True)

    return HttpResponse("Unrecognized announcement selection", status=400)


def send_announcement_grouped(announcements, phone_number_id, from_number, single_category=False):
    if not announcements.exists():
        send_whatsapp_message(phone_number_id, from_number, "📭 No announcements found for this category.")
        return HttpResponse("No announcements", status=200)

    grouped = defaultdict(list)
    for ann in announcements:
        category_name = ann.category.name if ann.category else "Uncategorized"
        grouped[category_name].append(ann)

    msg = "*📢 Latest Announcements:*\n\n"
    for category, anns in grouped.items():
        msg += f"*📚 {category}*\n"
        for ann in anns:
            msg += f"🔹 *{ann.title}*\n{ann.body}\n📅 {ann.created_at.strftime('%b %d, %Y')}\n\n"

    send_whatsapp_message(phone_number_id, from_number, msg.strip())
    return HttpResponse("Sent announcements", status=200)
