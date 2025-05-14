from django import forms
from apps.pages.models import Book,Suggestion,Author,Department

class SuggestionForm(forms.ModelForm):
    class Meta:
        model = Suggestion
        fields = ['suggestion_type', 'message']
        widgets = {
            'suggestion_type': forms.Select(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }



class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'department', 'isbn', 'published_date', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['author'].queryset = Author.objects.all()
        self.fields['department'].queryset = Department.objects.all()



