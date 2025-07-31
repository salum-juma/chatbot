from apps.pages.models import Announcement, AnnouncementCategory
from apps.pages.whatsapp.utils.whatsapp import send_announcement_category, send_whatsapp_list_message, send_whatsapp_message
from django.http import HttpResponse
from collections import defaultdict

def handle_announcement_menu(phone_number_id, from_number):
    print(f"📥 handle_announcement_menu called for: {from_number}")

    categories = AnnouncementCategory.objects.all()
    print(f"🔎 Found {categories.count()} announcement categories.")

    if not categories.exists():
        print("⚠️ No categories found.")
        send_whatsapp_message(phone_number_id, from_number, "📭 No categories available.")
        return HttpResponse("No categories", status=200)

    sections = [{
        "title": "📚 Choose Category",
        "rows": [
            {"id": f"ann_category_{cat.id}", "title": cat.name} for cat in categories
        ] + [{"id": "ann_view_all", "title": "📋 View All Announcements"}]
    }]

    print("✅ Sending category list to user.")
    send_announcement_category(
    phone_number_id,
    from_number,
    body="*📢 Announcements*\n\nTap a category below to view announcements:",
    button="📂 Categories",
    sections=sections
    )
    return HttpResponse("Sent announcement menu", status=200)



def handle_announcement_selection(text, phone_number_id, from_number):
    session = ChatSession.objects.get(phone_number=from_number)
    is_first_year = session.data.get('first_year', False)

    if text == "ann_view_all":
        announcements = Announcement.objects.all().order_by('-created_at')

        # ✅ Non-first-year students should not see first-year-only
        if not is_first_year:
            announcements = announcements.filter(first_year_only=False)

        print(f"📋 Viewing all announcements. Count: {announcements.count()}")
        return send_announcement_grouped(announcements, phone_number_id, from_number)

    elif text.startswith("ann_category_"):
        category_id = text.replace("ann_category_", "")
        announcements = Announcement.objects.filter(category_id=category_id).order_by('-created_at')

        if not is_first_year:
            announcements = announcements.filter(first_year_only=False)

        print(f"📂 Viewing announcements for category ID {category_id}. Count: {announcements.count()}")
        return send_announcement_grouped(announcements, phone_number_id, from_number, single_category=True)

    print("❌ Unrecognized announcement selection")
    return HttpResponse("Unrecognized announcement selection", status=400)



def send_announcement_grouped(announcements, phone_number_id, from_number, single_category=False):
    print(f"📤 send_announcement_grouped called. Count: {announcements.count()}")

    if not announcements.exists():
        print("⚠️ No announcements found.")
        send_whatsapp_message(phone_number_id, from_number, "📭 No announcements found for this category.")
        return HttpResponse("No announcements", status=200)

    grouped = defaultdict(list)
    for ann in announcements:
        category_name = ann.category.name if ann.category else "Uncategorized"
        grouped[category_name].append(ann)

    print(f"📦 Grouped announcements by {len(grouped)} categories")

    msg = "*📢 Latest Announcements:*\n\n"
    for category, anns in grouped.items():
        msg += f"*📚 {category}*\n"
        for ann in anns:
            msg += f"🔹 *{ann.title}*\n{ann.body}\n📅 {ann.created_at.strftime('%b %d, %Y')}\n\n"

    print("✅ Sending announcement message")
    send_whatsapp_message(phone_number_id, from_number, msg.strip())
    return HttpResponse("Sent announcements", status=200)

