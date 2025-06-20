import json
import os
from django.conf import settings
from django.shortcuts import render,redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.contrib import messages
from django.http import HttpResponse
from  apps.pages.helpers.library.forms import BookForm, PastPaperForm,SuggestionForm
from .models import Book, PastPaper,Suggestion,Author,Department,Student,User
from django.db.models import Q
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponseNotAllowed
from datetime import date
from django.shortcuts import get_object_or_404
from .models import Book, Penalty  
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

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


@require_POST
def toggle_status(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    book.status = 'Rendered' if book.status == 'Available' else 'Available'
    book.save()
    return redirect('view_books')


@require_POST
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    book.delete()
    return redirect('view_books')


def view_books(request):
    books = Book.objects.all()
    return render(request, 'librarian/view_books.html', {'books': books})


@csrf_exempt
def set_book_available(request, book_id):
    if request.method == 'POST':
        book = get_object_or_404(Book, id=book_id)

        # Check overdue condition
        if book.render_to and date.today() > book.render_to:
            overdue_days = (date.today() - book.render_to).days
            penalty_amount = overdue_days * 500

            if book.rendered_to:
                # Check if penalty exists
                existing_penalty = Penalty.objects.filter(
                    student=book.rendered_to,
                    book=book,
                    status='Unpaid'
                ).first()

                if existing_penalty:
                    # Mark the penalty as paid
                    existing_penalty.status = 'Paid'
                    existing_penalty.save()
                else:
                    # Create a new unpaid penalty
                    Penalty.objects.create(
                        student=book.rendered_to,
                        book=book,
                        days_late=overdue_days,
                        amount=penalty_amount,
                        reason=f"Returned {overdue_days} day(s) late",
                        status='Unpaid'
                    )

        # Reset book fields
        book.status = 'Available'
        book.rendered_to = None
        book.render_from = None
        book.render_to = None
        book.save()

        return JsonResponse({'success': 'Book marked as available'})

    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def render_book(request, book_id):
    if request.method == 'POST':
        book = get_object_or_404(Book, id=book_id)
        if book.status == 'Rendered':
            return JsonResponse({'error': 'Book already rendered'}, status=400)

        reg_number = request.POST.get('reg_number')
        render_from = request.POST.get('render_from')
        render_to = request.POST.get('render_to')

        try:
            student = Student.objects.get(reg_number=reg_number)
            book.rendered_to = student
            book.render_from = render_from
            book.render_to = render_to
            book.status = 'Rendered'
            book.save()
            return JsonResponse({'success': 'Book rendered successfully'})
        except Student.DoesNotExist:
            return JsonResponse({'error': 'Student not found'}, status=404)
    
    # If the request method is not POST, return a 405 Method Not Allowed response
    return HttpResponseNotAllowed(['POST'])
     
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
                'published_date': book.published_date.strftime('%Y-%m-%d') if book.published_date else '',
                'row_number': book.row_number or '',
                'rack_position': book.rack_position or '',
                'description': (book.description[:100] + '...') if book.description else '',
            })

    return JsonResponse({'results': results})

def view_penalties(request):
    # Only unpaid penalties
    penalties = Penalty.objects.select_related('student', 'book').order_by('-created_at')
    return render(request, 'librarian/view_penalties.html', {'penalties': penalties})

def past_papers(request):
    papers = PastPaper.objects.all().order_by('-uploaded_at')
    return render(request, 'librarian/past_papers.html', {'papers': papers})

def add_past_paper(request):
    departments = Department.objects.all()
    if request.method == 'POST':
        form = PastPaperForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_file = request.FILES['pdf']  # Replace with your actual field name

            # Define path to save file
            save_path = os.path.join(settings.BASE_DIR, 'static', 'pdf', pdf_file.name)

            # Save file manually
            path = default_storage.save(save_path, ContentFile(pdf_file.read()))

            # Now save the model but **without** the file field or set file field path manually if needed
            past_paper = form.save(commit=False)
            past_paper.pdf_field = 'pdf/' + pdf_file.name  # Assuming your model's field stores relative path inside static
            past_paper.save()

            return redirect('past_paper_list')
    else:
        form = PastPaperForm()
    return render(request, 'librarian/add_past_paper.html', {'form': form, 'departments': departments})

def past_paper_list(request):
    papers = PastPaper.objects.all()

    department = request.GET.get('department')
    year = request.GET.get('academic_year')
    pub_year = request.GET.get('published_year')

    # Convert department to int if possible, else None
    try:
        department_int = int(department) if department else None
    except (ValueError, TypeError):
        department_int = None

    if department_int:
        papers = papers.filter(department__id=department_int)
    if year:
        papers = papers.filter(academic_year=year)
    if pub_year:
        papers = papers.filter(published_year=pub_year)

    context = {
        'papers': papers,
        'departments': Department.objects.all(),
        'selected_department': str(department) if department else '',  # convert to string
        'selected_year': year,
        'selected_pub_year': pub_year,
    }

    return render(request, 'librarian/past_paper_list.html', context)


def delete_past_paper(request, pk):
    paper = get_object_or_404(PastPaper, pk=pk)
    paper.delete()
    messages.success(request, "Past paper deleted.")
    return redirect('past_paper_list')