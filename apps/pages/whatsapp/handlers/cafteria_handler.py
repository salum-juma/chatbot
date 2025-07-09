import uuid
from django.http import HttpResponse
from apps.pages.models import MealOrder, MealOrderItem, MenuItem, Student
from apps.pages.whatsapp.utils.whatsapp import send_whatsapp_list_message, send_whatsapp_message

def handle_cafeteria_flow(text, phone_number_id, from_number, session):
    print(f"[CAFETERIA] Handling text='{text}', stage='{session.stage}'")

    if text == "student_cafeteria":
        session.stage = 'cafeteria_selecting_item'
        session.save()
        print("[CAFETERIA] Sending menu items")
        return send_menu_items(phone_number_id, from_number)

    elif session.stage == 'cafeteria_selecting_item' and text.startswith("meal_select_"):
        meal_id = text.replace("meal_select_", "")
        session.stage = 'cafeteria_entering_quantity'
        session.temp_meal_id = meal_id
        session.save()

        meal = MenuItem.objects.get(id=meal_id)
        send_whatsapp_message(
            phone_number_id,
            from_number,
            f"🍽️ How many servings of *{meal.name}* would you like?\n\n👉 Please enter a number (e.g. 1, 2, 3...)"
        )

        print("[CAFETERIA] Asked for quantity")
        return HttpResponse("Asking quantity", status=200)

    elif session.stage == 'cafeteria_selecting_item' and text.startswith("meal_category_"):
        parent_id = text.replace("meal_category_", "")
        sub_items = MenuItem.objects.filter(parent_id=parent_id, available=True)

        if not sub_items.exists():
            send_whatsapp_message(phone_number_id, from_number, "⚠️ No options found under this category.")
            return HttpResponse("No subitems", status=200)

        rows = []
        for sub in sub_items:
            rows.append({
                "id": f"meal_select_{sub.id}",
                "title": sub.name,
                "description": f"TZS {sub.price}"
            })

        send_whatsapp_list_message(
            phone_number_id,
            from_number,
            body="🍛 *Meal Options*\nPlease choose a variation:",
            sections=[{
                "title": "Options",
                "rows": rows
            }]
        )
        return HttpResponse("Sent subitem options", status=200)

    elif session.stage == 'cafeteria_entering_quantity' and text.isdigit():
        quantity = int(text)
        meal = MenuItem.objects.get(id=session.temp_meal_id)
        cart = session.temp_data or []
        cart.append({'meal_id': meal.id, 'meal_name': meal.name, 'quantity': quantity, 'price': float(meal.price)})
        session.temp_data = cart
        session.stage = 'cafeteria_adding_more_or_done'
        session.save()

        send_whatsapp_list_message(
            phone_number_id,
            from_number,
            body=f"✅ Added *{quantity} {meal.name}* to your order.\n\nWould you like to:",
            sections=[{
                "title": "Next Step",
                "rows": [
                    {"id": "add_another_item", "title": "➕ Add another item"},
                    {"id": "finish_order", "title": "✅ Finish and Pay"}
                ]
            }]
        )
        print("[CAFETERIA] Asked add more or finish")
        return HttpResponse("Ask add more or finish", status=200)

    elif session.stage == 'cafeteria_adding_more_or_done':
        if text == "add_another_item":
            session.stage = 'cafeteria_selecting_item'
            session.save()
            print("[CAFETERIA] Adding another item - sending menu")
            return send_menu_items(phone_number_id, from_number)

        elif text == "finish_order":
            cart = session.temp_data or []
            if not cart:
                send_whatsapp_message(phone_number_id, from_number, "⚠️ Your cart is empty.")
                return HttpResponse("Cart empty", status=200)

            try:
                student = Student.objects.get(reg_number=session.reg_number)
            except Student.DoesNotExist:
                send_whatsapp_message(phone_number_id, from_number, "⚠️ You need to log in first before placing an order.")
                return HttpResponse("Student not found", status=400)

            ref = uuid.uuid4().hex[:6].upper()
            total = sum(item['price'] * item['quantity'] for item in cart)

            order = MealOrder.objects.create(
                student=student,
                phone_number=from_number,
                phone_number_id=phone_number_id,
                total_amount=total,
                status='pending',
                token=None,
                transaction_message=None
            )

            for item in cart:
                meal = MenuItem.objects.get(id=item['meal_id'])
                MealOrderItem.objects.create(order=order, menu_item=meal, quantity=item['quantity'])

            session.stage = 'cafeteria_waiting_payment_message'
            session.temp_meal_id = None
            session.temp_data = None
            session.temp_order_id = order.id
            session.save()

            msg = f"💵 *Order Summary:*\n"
            for item in cart:
                msg += f"- {item['meal_name']} x {item['quantity']} = TZS {item['quantity'] * item['price']}\n"
            msg += f"\n*Total:* TZS {total}\n"
            msg += f"\n✅ Please pay to M-Pesa number: 07XXXXXXXX\n🧾 Then reply with the *transaction message* you receive."

            send_whatsapp_message(phone_number_id, from_number, msg)
            return HttpResponse("Order summary sent, awaiting transaction message", status=200)

    elif session.stage == 'cafeteria_waiting_payment_message':
        transaction_msg = text.strip()
        try:
            order = MealOrder.objects.get(id=session.temp_order_id)
            order.transaction_message = transaction_msg
            order.status = 'paid'
            order.save()
            session.stage = 'cafeteria_done'
            session.temp_order_id = None
            session.save()
            send_whatsapp_message(phone_number_id, from_number, "✅ Thank you! Your transaction has been received and is pending verification by the canteen staff.")
            return HttpResponse("Transaction received", status=200)
        except MealOrder.DoesNotExist:
            send_whatsapp_message(phone_number_id, from_number, "⚠️ Could not find your order. Please try again.")
            return HttpResponse("Order not found", status=400)

    print("[CAFETERIA] No matching condition - returning 200 OK")
    return HttpResponse("OK", status=200)

def send_menu_items(phone_number_id, from_number):
    top_level_items = MenuItem.objects.filter(parent__isnull=True, available=True)
    rows = []
    for item in top_level_items:
        if item.subitems.filter(available=True).exists():
            rows.append({
                "id": f"meal_category_{item.id}",
                "title": item.name,
                "description": "➡️ View options"
            })
        else:
            rows.append({
                "id": f"meal_select_{item.id}",
                "title": item.name,
                "description": f"TZS {item.price}"
            })

    send_whatsapp_list_message(
        phone_number_id,
        from_number,
        body="🍽️ *Available Meals*\nPlease choose one:",
        sections=[{
            "title": "Main Menu",
            "rows": rows
        }]
    )
    print("[CAFETERIA] Sent menu list message")
    return HttpResponse("Menu sent", status=200)
