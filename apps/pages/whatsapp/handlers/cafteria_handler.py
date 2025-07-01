# handlers/cafeteria_handler.py

import uuid
from django.http import HttpResponse
from apps.pages.models import MealOrder, MealOrderItem, MenuItem
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

            # Create order
            ref = uuid.uuid4().hex[:6].upper()
            order = MealOrder.objects.create(phone_number=from_number, payment_reference=ref)
            total = 0
            for item in cart:
                meal = MenuItem.objects.get(id=item['meal_id'])
                MealOrderItem.objects.create(order=order, meal=meal, quantity=item['quantity'])
                total += meal.price * item['quantity']

            session.stage = 'cafeteria_payment_pending'
            session.temp_meal_id = None
            session.temp_data = None
            session.save()

            msg = f"💵 *Order Summary:*\n"
            for item in cart:
                msg += f"- {item['meal_name']} x {item['quantity']} = TZS {item['quantity'] * item['price']}\n"
            msg += f"\n*Total:* TZS {total}\n"
            msg += f"\n✅ Pay via M-Pesa to: 07XXXXXXXX\n🧾 Use reference: *{ref}*"

            send_whatsapp_message(phone_number_id, from_number, msg)
            print("[CAFETERIA] Order placed and payment info sent")
            return HttpResponse("Order placed", status=200)

    # If no condition matched, return a default HttpResponse (avoid None)
    print("[CAFETERIA] No matching condition - returning 200 OK")
    return HttpResponse("OK", status=200)


def send_menu_items(phone_number_id, from_number):
    menu_items = MenuItem.objects.filter(available=True)
    rows = []
    for item in menu_items:
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
            "title": "Menu Items",
            "rows": rows
        }]
    )
    print("[CAFETERIA] Sent menu list message")
    return HttpResponse("Menu sent", status=200)
