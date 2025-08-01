# Generated by Django 4.2.9 on 2025-07-01 16:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("pages", "0002_menuitem"),
    ]

    operations = [
        migrations.CreateModel(
            name="MealOrder",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("ordered_at", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "total_amount",
                    models.DecimalField(decimal_places=2, default=0.0, max_digits=8),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("paid", "Paid"),
                            ("verified", "Verified"),
                        ],
                        default="pending",
                        max_length=10,
                    ),
                ),
                ("token", models.CharField(blank=True, max_length=10, null=True)),
                ("verified_at", models.DateTimeField(blank=True, null=True)),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="pages.student"
                    ),
                ),
                (
                    "verified_by",
                    models.ForeignKey(
                        blank=True,
                        limit_choices_to={"role": "librarian"},
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="MealOrderItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("quantity", models.PositiveIntegerField(default=1)),
                (
                    "menu_item",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="pages.menuitem"
                    ),
                ),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="pages.mealorder",
                    ),
                ),
            ],
        ),
    ]
