from django.shortcuts import render,redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import HttpResponse
from  apps.pages.helpers.library.forms import BookForm
from .models import Book

def index(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)                
                if user.role == 'student':
                    return HttpResponse("student")  
                elif user.role == 'librarian':
                    return HttpResponse("librarian")  
                else:
                    return HttpResponse("default")  
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'auth/login.html', {'form': form})



def home(request):
    user = request.user
    if user.role == 'librarian':
        return render(request, 'librarian/home.html', {'name': user.full_name})
    elif user.role == 'student':
        return render(request, 'student/home.html', {'name': user.full_name})
    else:
        return HttpResponse(f"You are logged in as a {user.role}.")



def student_home(request):
    return render(request, 'student/home.html')


def librarian_home(request):
    return render(request, 'librarian/home.html')


def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)  
        if form.is_valid():
            form.save()  
            return redirect('view_books')  
    else:
        form = BookForm()  

    return render(request, 'librarian/add_book.html', {'form': form})

def view_books(request):
    books = Book.objects.all()
    return render(request, 'librarian/view_books.html', {'books': books})