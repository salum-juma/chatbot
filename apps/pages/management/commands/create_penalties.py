from django.core.management.base import BaseCommand
from datetime import date
from apps.pages.models import Book, Penalty

class Command(BaseCommand):
    help = 'Automatically create penalties for overdue books'

    def handle(self, *args, **kwargs):
        today = date.today()
        overdue_books = Book.objects.filter(status='Rendered', render_to__lt=today, rendered_to__isnull=False)

        for book in overdue_books:
            overdue_days = (today - book.render_to).days
            penalty_amount = overdue_days * 500  # TZS per day

            # Check if penalty already exists
            if not Penalty.objects.filter(book=book, student=book.rendered_to).exists():
                Penalty.objects.create(
                    student=book.rendered_to,
                    book=book,
                    days_late=overdue_days,
                    amount=penalty_amount,
                )
                self.stdout.write(self.style.SUCCESS(
                    f"Penalty created for '{book.title}' (Student: {book.rendered_to.reg_number})"
                ))
            else:
                self.stdout.write(f"Penalty already exists for '{book.title}' and student {book.rendered_to.reg_number}")
