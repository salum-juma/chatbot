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
def get_borrowed_books(request):
    try:
        student = request.user.student_profile  # Use your related_name here
    except Student.DoesNotExist:
        return render(request, 'student/no_student.html', {'message': 'You are not registered as a student.'})

    borrowed_books = Book.objects.filter(rendered_to=student)
    print(borrowed_books)
    return render(request, 'student/borrowed_books.html', {'borrowed_books': borrowed_books})