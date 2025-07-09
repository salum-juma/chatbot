import random
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from apps.pages.models import Author, Book, Department, MealOrder, MealOrderItem, MenuItem
from apps.pages.whatsapp.utils.whatsapp import send_whatsapp_message
from django.views.decorators.csrf import csrf_exempt


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
            Q(student__reg_number__icontains=query) |
            Q(id__icontains=query) |
            Q(token__icontains=query) |
            Q(transaction_message__icontains=query)
        )

    orders = orders.order_by('-ordered_at')

    for order in orders:
        order.items_list = MealOrderItem.objects.filter(order=order)
        order.total = sum(item.menu_item.price * item.quantity for item in order.items_list)

    return render(request, 'canteen/orders.html', {'orders': orders, 'query': query})


@csrf_exempt
def approve_order(request, order_id):
    order = get_object_or_404(MealOrder, id=order_id)

    if request.method == 'POST':
        ready_in_minutes = request.POST.get('ready_in_minutes')
        try:
            token = f"TKN{random.randint(1000,9999)}"
            order.token = token
            order.status = 'approved'
            order.ready_time = timezone.now() + timezone.timedelta(minutes=int(ready_in_minutes))
            order.save()

            msg = (
                f"✅ Your food order has been approved and will be ready in about {ready_in_minutes} minutes.\n"
                f"📌 Please come with your token number: *{token}* to collect your meal."
            )
            if order.phone_number_id:
                send_whatsapp_message(order.phone_number_id, order.phone_number, msg)
            else:
                print("Warning: phone_number_id missing for order", order.id)

            messages.success(request, f"Order approved and WhatsApp message sent to {order.phone_number}.")
        except Exception as e:
            messages.error(request, f"Error approving order: {str(e)}")
        return redirect('orders_page')

    return redirect('orders_page')


@csrf_exempt
def update_ready_time(request, order_id):
    order = get_object_or_404(MealOrder, id=order_id)
    if request.method == 'POST':
        ready_in_minutes = request.POST.get('ready_in_minutes')
        try:
            order.ready_time = timezone.now() + timezone.timedelta(minutes=int(ready_in_minutes))
            order.save()
            messages.success(request, f"Ready time updated for order #{order.id}.")
        except Exception as e:
            messages.error(request, f"Error updating ready time: {str(e)}")
        return redirect('orders_page')


@csrf_exempt
def mark_order_served(request, order_id):
    order = get_object_or_404(MealOrder, id=order_id)

    if order.status != 'approved':
        messages.error(request, "Only approved orders can be marked as served.")
        return redirect('orders_page')

    order.status = 'served'
    order.save()

    messages.success(request, f"Order #{order.id} marked as served.")
    return redirect('orders_page')
