# Generated by Django 4.2.9 on 2025-07-09 08:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pages", "0006_remove_mealorder_payment_reference"),
    ]

    operations = [
        migrations.AddField(
            model_name="mealorder",
            name="transaction_message",
            field=models.TextField(blank=True, null=True),
        ),
    ]
