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
            # Extract cleaned form data
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            role = form.cleaned_data['role']
            department = form.cleaned_data.get('department')
            new_department = request.POST.get('new_department', '').strip()

            # Handle new department creation if provided
            if new_department:
                department, _ = Department.objects.get_or_create(name=new_department)

            # Determine registration number
            if role == 'student':
                last_user = User.objects.filter(registration_no__startswith='2001').order_by('-registration_no').first()
                if last_user:
                    last_reg_no = int(last_user.registration_no)
                    new_reg_no = str(last_reg_no + 1)
                else:
                    new_reg_no = '20010101'
            else:
                new_reg_no = username  # Use provided username for non-students

            # Create user
            user = User.objects.create_user(
                registration_no=new_reg_no,
                password=password,
                email=email,
                full_name=username,
                role=role
            )

            # Optionally associate department (if needed in your model)
            if department:
                pass  # Extend model logic if you want to save department info

            if role == 'student':
                Student.objects.create(
                user=user,
                enrollment_year=2025,  # Optionally make dynamic
                program="Default Program",  # Optionally make dynamic
                reg_number=new_reg_no,
                name=username,
                department=department.name if department else 'General'
            )

            messages.success(request, "User created successfully.")
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