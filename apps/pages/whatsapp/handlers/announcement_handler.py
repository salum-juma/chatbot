from collections import defaultdict
from django.http import HttpResponse
from apps.pages.models import Announcement, AnnouncementCategory, Student
from apps.pages.whatsapp.utils.whatsapp import (
    send_announcement_category,
    send_whatsapp_message
)

# --- PHONE NORMALIZATION UTILS ---
# test
def normalize_to_last9(phone_number: str):
    """Return last 9 digits for DB matching like 0620416606."""
    if not phone_number:
        return None
    digits = phone_number.replace("+", "").replace(" ", "")
    return digits[-9:]  # Only last 9 digits used for comparison

def is_first_year_student(from_number):
    """Check DB if phone number belongs to a first-year student."""
    last9 = normalize_to_last9(from_number)
    student = Student.objects.filter(phone_number__endswith=last9).first()
    
    if student and student.year and student.year.number == 1:
        print(f"🎓 {from_number} (last9:{last9}) is a first-year student")
        return True
    
    print(f"🎓 {from_number} (last9:{last9}) is NOT a first-year student")
    return False

# --- MAIN HANDLERS ---

def handle_announcement_menu(phone_number_id, from_number):
    print(f"\n📥 handle_announcement_menu called for: {from_number}")

    # Check DB for first-year status
    is_first_year = is_first_year_student(from_number)

    # ✅ First-year students: directly send their announcements
    if is_first_year:
        announcements = Announcement.objects.filter(first_year_only=True).order_by('-created_at')
        print(f"📋 Found {announcements.count()} first-year announcements")
        if announcements.exists():
            return send_announcement_grouped(announcements, phone_number_id, from_number)
        else:
            send_whatsapp_message(phone_number_id, from_number, "📭 No announcements for first-year students yet.")
            return HttpResponse("No first-year announcements", status=200)

    # 🔹 Non-first-year: show category menu
    categories = AnnouncementCategory.objects.all()
    print(f"🔎 Found {categories.count()} announcement categories for non-first-year student.")

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
    is_first_year = is_first_year_student(from_number)
    print(f"\n📥 handle_announcement_selection: {text} for {from_number}")
    print(f"🎓 First-year status: {is_first_year}")

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
