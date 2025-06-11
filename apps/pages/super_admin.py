from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.db.models import Q

from apps.pages.helpers.library.forms import BookForm, SuggestionForm
from apps.pages.helpers.super_admin.super_admin_form import AddUserForm
from apps.pages.models import Book, Suggestion, Author, Department, User, Student
from apps.pages.whatsapp.utils.sms_logic import send_sms


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
                Student.objects.create(
                    user=user,
                    enrollment_year=2025,
                    program='Default Program',
                    reg_number=reg_number,
                    name=full_name,
                    department=department.name if department else 'General',
                    phone_number=phone_number
                )

            # Prepare and send SMS
            sms_message = (
                f"Welcome {full_name}! Your registration number is {reg_number}. "
                f"Your password is: {password}. Please keep it safe."
            )
            sms_sent = send_sms(phone_number, sms_message)

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
