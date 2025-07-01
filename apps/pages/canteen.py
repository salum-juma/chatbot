from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from apps.pages.models import Author, Book, Department, MenuItem


def canteen_home(request):
    total_books = Book.objects.count()  
    total_authors = Author.objects.count()  
    total_departments = Department.objects.count()  

    return render(request, 'canteen/canteen_index.html', {
        'name': 'library',
        'total_books': total_books,
        'total_authors': total_authors,
        'total_departments': total_departments,
    })


def menu_page(request):
    menu_items = MenuItem.objects.all().order_by('-created_at')
    return render(request, 'canteen/menu_page.html', {
        'menu_items': menu_items
    })


def add_menu_item(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        available = request.POST.get('available') == 'on'

        MenuItem.objects.create(
            name=name,
            description=description,
            price=price,
            available=available
        )
        messages.success(request, f"{name} added to the menu.")
        return redirect('menu_page')

    return render(request, 'canteen/add_menu_item.html')


def delete_menu_item(request, pk):
    paper = get_object_or_404(MenuItem, pk=pk)
    paper.delete()
    messages.success(request, "Menu Item deleted.")
    return redirect('menu_page')