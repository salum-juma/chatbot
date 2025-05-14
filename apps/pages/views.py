from django.shortcuts import render,redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.contrib import messages
from django.http import HttpResponse
from  apps.pages.helpers.library.forms import BookForm,SuggestionForm
from .models import Book,Suggestion
from django.db.models import Q


def search_books(request):
    query = request.GET.get('q', '')
    results = []

    if query:
        books = Book.objects.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(department__icontains=query)
        )
        for book in books:
            results.append({
                'title': book.title,
                'author': book.author,
                'department': book.department,
                'isbn': book.isbn,
                'published_date': book.published_date.strftime('%Y-%m-%d')
            })

    return JsonResponse({'results': results})

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

def suggestion_page(request):
    if request.method == 'POST':
        form = SuggestionForm(request.POST)
        if form.is_valid():
            suggestion = form.save(commit=False)
            if request.user.is_authenticated:
                suggestion.user = request.user  # optional
            suggestion.save()
            messages.success(request, 'Thank you for your suggestion!')
            return redirect('suggestion_page')
    else:
        form = SuggestionForm()
    return render(request, 'common/suggestion_form.html', {'form': form})

def view_suggestions(request):
    suggestions = Suggestion.objects.all()
    return render(request, 'common/view_suggestions.html', {'suggestions': suggestions})


def custom_logout(request):
    logout(request)  
    return HttpResponseRedirect('/login/') 