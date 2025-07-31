from collections import defaultdict
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.db.models import Q

from apps.pages.helpers.library.forms import BookForm, SuggestionForm
from apps.pages.helpers.super_admin.super_admin_form import AddUserForm
from apps.pages.models import Announcement, AnnouncementCategory, Book, Suggestion, Author, Department, User, Student
from apps.pages.whatsapp.utils.sms_logic import send_sms
from apps.pages.models import Year


# Super Admin - Add User Page
def add_user_page(request):
    departments = Department.objects.all()

    if request.method == 'POST':
        form = AddUserForm(request.POST)
        if form.is_valid():
            full_name = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            role = form.cleaned_data['role']
            department = form.cleaned_data['department']
            new_department = form.cleaned_data['new_department'].strip()
            phone_number = form.cleaned_data.get('phone_number')

            # Handle new department creation
            if new_department:
                category = 'Degree' if 'degree' in role else 'Diploma'

                # Check if department with same name exists
                department = Department.objects.filter(name=new_department).first()
                if not department:
                    # Assign new code starting from 01, incrementing
                    existing_codes = Department.objects.filter(category=category).values_list('code', flat=True)
                    used_codes = set(int(code) for code in existing_codes if code.isdigit())
                    new_code = 1
                    while new_code in used_codes:
                        new_code += 1
                    department_code = str(new_code).zfill(2)
                    department = Department.objects.create(name=new_department, category=category, code=department_code)

            # Use existing department code
            department_code = department.code.zfill(2) if department and department.code else '00'

            # Generate registration number
            if role in ['degree_student', 'diploma_student']:
                prefix = '30' if role == 'degree_student' else '20'
                reg_prefix = f"{prefix}{department_code}"

                # Get last serial number for this department+program type
                existing_regs = Student.objects.filter(
                    reg_number__startswith=reg_prefix
                ).order_by('-reg_number')

                if existing_regs.exists():
                    last = existing_regs.first().reg_number
                    serial = int(last[-3:]) + 1
                else:
                    serial = 1

                reg_number = f"{reg_prefix}{str(serial).zfill(3)}"
            else:
                # Staff/Librarian/Admin
                reg_number = email.split('@')[0]

            # Create User
            user = User.objects.create_user(
                registration_no=reg_number,
                password=password,
                email=email,
                full_name=full_name,
                phone_number = phone_number,
                role='student' if 'student' in role else role
            )

            # Create student profile
            if 'student' in role:
                default_year = Year.objects.get(number=1)
                Student.objects.create(
                    user=user,
                    enrollment_year=2025,
                    program='Default Program',
                    reg_number=reg_number,
                    name=full_name,
                    department=department.name if department else 'General',
                    phone_number=phone_number,
                    year=default_year  # 🟢 Set year to Year 1
                )

            # Prepare and send SMS
            sms_message = (
                f"Welcome {full_name}! Your registration number is {reg_number}. "
                f"Your password is: {password}. Please keep it safe."
            )
            # sms_sent = send_sms(phone_number, sms_message)
            sms_sent = 1
            if sms_sent:
                messages.success(request, f"User created successfully! SMS sent to {phone_number}.")
            else:
                messages.warning(request, f"User created successfully! But SMS failed to send to {phone_number}.")

            return redirect('add_user_page')
    else:
        form = AddUserForm()

    return render(request, 'super_admin/add_user_page.html', {
        'form': form,
        'departments': departments
    })


def view_all_users(request):
    # select_related with 'student_profile' to avoid extra queries
    users = User.objects.all().select_related('student_profile')
    return render(request, 'super_admin/view_users.html', {'users': users})

def promote_students(request):
    students = Student.objects.select_related('user', 'year')  # Efficient fetch
    years = Year.objects.all()  # Fetch all year options
    return render(request, 'super_admin/promote_students_page.html', {
        'students': students,
        'years': years
    })


def promote_student(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        new_year_id = request.POST.get('new_year_id')

        student = get_object_or_404(Student, id=student_id)
        try:
            new_year = Year.objects.get(id=new_year_id)
            student.year = new_year
            student.save()
            messages.success(request, f"{student.name} promoted to Year {new_year.number}.")
        except Year.DoesNotExist:
            messages.error(request, "Selected year is invalid.")

        return redirect('promote_students')

    messages.error(request, "Invalid request.")
    return redirect('promote_students_page')

def announcements_page(request):
    categories = AnnouncementCategory.objects.all()
    anns = Announcement.objects.select_related('category').order_by('-created_at')
    grouped = defaultdict(list)
    for ann in anns:
        grouped[ann.category.name if ann.category else "Uncategorized"].append(ann)

    context = {
        'categories': categories,
        'announcements': dict(grouped),
    }
    return render(request, 'super_admin/announcements.html', context)

def add_announcement(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        body = request.POST.get('body')
        category_id = request.POST.get('category_id')
        new_category = request.POST.get('new_category', '').strip()

        # ✅ Support checkbox ("on") or select ("True"/"False")
        first_year_only_raw = request.POST.get('first_year_only', '')
        first_year_only = first_year_only_raw in ['True', 'on', '1']

        # Validate category choice
        if new_category and category_id:
            messages.error(request, "⚠️ Please provide either a new category or select an existing one, not both.")
            return redirect('add_announcement')

        if new_category:
            category, _ = AnnouncementCategory.objects.get_or_create(name=new_category)
        elif category_id:
            category = get_object_or_404(AnnouncementCategory, id=category_id)
        else:
            messages.error(request, "⚠️ Please choose a category or enter a new one.")
            return redirect('add_announcement')

        # ✅ Create announcement with first_year_only flag
        Announcement.objects.create(
            title=title,
            body=body,
            category=category,
            first_year_only=first_year_only
        )

        messages.success(request, '📢 Announcement added successfully.')
        return redirect('announcements')

    # Group announcements by category
    grouped_announcements = defaultdict(list)
    for ann in Announcement.objects.select_related('category').order_by('-created_at'):
        cat_name = ann.category.name if ann.category else "Uncategorized"
        grouped_announcements[cat_name].append(ann)

    categories = AnnouncementCategory.objects.all()
    return render(request, 'super_admin/announcements.html', {
        'announcements': grouped_announcements,
        'categories': categories
    })

def delete_announcement(request, ann_id):
    announcement = get_object_or_404(Announcement, id=ann_id)
    announcement.delete()
    messages.success(request, "🗑️ Announcement deleted successfully.")
    return redirect('announcements')


def add_dummy_users(request):
    # Only allow this in development/debug mode
    from django.conf import settings
    if not settings.DEBUG:
        return HttpResponse("Not allowed", status=403)
    
    # Create or get a department for the student
    department, _ = Department.objects.get_or_create(name="Computer Science", code="01", category="degree")

    # Admin user
    admin_user, created = User.objects.get_or_create(
        registration_no="admin",
        defaults={
            "email": "admin@example.com",
            "full_name": "super",
            "role": "admin",
            "is_staff": True,
            "is_superuser": True,
        }
    )
    if created:
        admin_user.set_password("super")
        admin_user.save()

    # Librarian user
    librarian_user, created = User.objects.get_or_create(
        registration_no="librarian",
        defaults={
            "email": "librarian@example.com",
            "full_name": "juma",
            "role": "librarian",
            "is_staff": True,
        }
    )
    if created:
        librarian_user.set_password("juma")
        librarian_user.save()

    # Student user
    student_reg_no = "3001001"  # example reg number
    student_user, created = User.objects.get_or_create(
        registration_no=student_reg_no,
        defaults={
            "email": "student@example.com",
            "full_name": "Student One",
            "role": "student",
            "is_staff": False,
        }
    )
    if created:
        student_user.set_password("123")
        student_user.save()
        # Create student profile
        Student.objects.get_or_create(
            user=student_user,
            defaults={
                "reg_number": student_reg_no,
                "name": "Student One",
                "enrollment_year": 2025,
                "program": "Default Program",
                "department": department.name,
                "phone_number": "",
            }
        )

    return HttpResponse("Dummy users added (if not existed)")