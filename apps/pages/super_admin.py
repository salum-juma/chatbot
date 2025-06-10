from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.db.models import Q

from apps.pages.helpers.library.forms import BookForm, SuggestionForm
from apps.pages.helpers.super_admin.super_admin_form import AddUserForm
from apps.pages.models import Book, Suggestion, Author, Department, User, Student


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
                department, _ = Department.objects.get_or_create(name=new_department, defaults={
                    'code': '99',  # You may auto-generate or assign dynamically
                    'category': category
                })

            # Determine department code
            department_code = department.code if department else '00'

            # Generate student registration number
            if role in ['degree_student', 'diploma_student']:
                prefix = '30' if role == 'degree_student' else '20'
                existing_regs = Student.objects.filter(reg_number__startswith=f"{prefix}{department_code}").order_by('-reg_number')
                if existing_regs.exists():
                    last = existing_regs.first().reg_number
                    serial = int(last[-3:]) + 1
                else:
                    serial = 1
                reg_number = f"{prefix}{department_code}{str(serial).zfill(3)}"
            else:
                reg_number = email.split('@')[0]  # For staff/librarian/admin, use email prefix or any logic

            # Create User
            user = User.objects.create_user(
                registration_no=reg_number,
                password=password,
                email=email,
                full_name=full_name,
                role='student' if 'student' in role else role
            )

            # Create Student profile if role is student
            if 'student' in role:
                Student.objects.create(
                    user=user,
                    enrollment_year=2025,
                    program='Default Program',
                    reg_number=reg_number,
                    name=full_name,
                    department=department.name if department else 'General',
                    phone_number=phone_number or ''
                )

            messages.success(request, f"User {full_name} created successfully with Reg No: {reg_number}.")
            return redirect('add_user_page')
    else:
        form = AddUserForm()

    return render(request, 'super_admin/add_user_page.html', {
        'form': form,
        'departments': departments
    })

def view_all_users(request):
    users = User.objects.all()
    return render(request, 'super_admin/view_users.html', {'users': users})