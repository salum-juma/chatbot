import random
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from apps.pages.models import Author, Book, Department, MealOrder, MealOrderItem, MenuItem
from django.db.models import Q

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


def orders_page(request):
    query = request.GET.get('q', '')
    orders = MealOrder.objects.exclude(status='served')

    if query:
        orders = orders.filter(
            Q(phone_number__icontains=query) |
            Q(id__icontains=query) |
            Q(token__icontains=query)
        )

    orders = orders.order_by('-ordered_at')
    for order in orders:
        order.items_list = MealOrderItem.objects.filter(order=order)
        order.total = sum(item.meal.price * item.quantity for item in order.items_list)
    return render(request, 'canteen/orders.html', {'orders': orders, 'query': query})


def approve_order(request, order_id):
    order = get_object_or_404(MealOrder, id=order_id)
    token = f"TKN{random.randint(1000,9999)}"
    order.token = token
    order.status = 'approved'
    order.save()

    # Send SMS (dummy logic for now, integrate with SMS gateway)
    message = f"Your food order has been approved. Use token {token} to collect."
    print(f"Sending SMS to {order.phone_number}: {message}")

    messages.success(request, f"Order approved and token sent to {order.phone_number}.")
    return redirect('orders_page')


def mark_order_served(request, order_id):
    order = get_object_or_404(MealOrder, id=order_id)

    if order.status != 'approved':
        messages.error(request, "Only approved orders can be marked as served.")
        return redirect('orders_page')

    order.status = 'served'
    order.save()

    messages.success(request, f"Order #{order.id} marked as served.")
    return redirect('orders_page')
