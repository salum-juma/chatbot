from django.shortcuts import render,redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.contrib import messages
from django.http import HttpResponse
from  apps.pages.helpers.library.forms import BookForm,SuggestionForm
from .models import Book,Suggestion,Author,Department
from django.db.models import Q
from django.shortcuts import redirect


def search_books(request):
    query = request.GET.get('q', '')
    results = []

    if query:
        
        books = Book.objects.filter(
            Q(title__icontains=query) |
            Q(author__name__icontains=query) |  
            Q(department__name__icontains=query)  
        )
        for book in books:
            results.append({
                'title': book.title,
                'author': book.author.name,  
                'department': book.department.name,  
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
          return redirect('librarian/home')
        
    elif user.role == 'student':
        return render(request, 'student/home.html', {'name': user.full_name})
    else:
        return HttpResponse(f"You are logged in as a {user.role}.")



def student_home(request):
    return render(request, 'student/home.html')


def librarian_home(request):
    total_books = Book.objects.count()  
    total_authors = Author.objects.count()  
    total_departments = Department.objects.count()  

    return render(request, 'librarian/home.html', {
        'name': 'library',
        'total_books': total_books,
        'total_authors': total_authors,
        'total_departments': total_departments,
    })



def add_book(request):
    authors = Author.objects.all()
    departments = Department.objects.all()
    form = BookForm(request.POST or None)
    
    if request.method == 'POST':
        new_author = request.POST.get('new_author')
        new_department = request.POST.get('new_department')

        
        if new_author:
            author, created = Author.objects.get_or_create(name=new_author)
        else:
            author_id = request.POST.get('author')
            if author_id:
                try:
                    author = Author.objects.get(id=author_id)
                except Author.DoesNotExist:
                    author = None
            else:
                author = None

        
        if new_department:
            department, created = Department.objects.get_or_create(name=new_department)
        else:
            department_id = request.POST.get('department')
            if department_id:
                try:
                    department = Department.objects.get(id=department_id)
                except Department.DoesNotExist:
                    department = None
            else:
                department = None

        if form.is_valid():
            book = form.save(commit=False)
            book.author = author  
            book.department = department  
            book.save()
            return redirect('view_books')  

        else:
            print(form.errors)  

    return render(request, 'librarian/add_book.html', {'form': form, 'authors': authors, 'departments': departments})






def view_books(request):
    books = Book.objects.all()
    return render(request, 'librarian/view_books.html', {'books': books})

def suggestion_page(request):
    if request.method == 'POST':
        form = SuggestionForm(request.POST)
        if form.is_valid():
            suggestion = form.save(commit=False)
            if request.user.is_authenticated:
                suggestion.user = request.user  
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