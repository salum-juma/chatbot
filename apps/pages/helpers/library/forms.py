from django import forms
from apps.pages.models import Book

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'department', 'isbn', 'published_date', 'description']
