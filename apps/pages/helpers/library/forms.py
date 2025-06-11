from datetime import date
from django import forms
from apps.pages.models import Book, PastPaper,Suggestion,Author,Department

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
        fields = [
            'title', 'author', 'department',
            'isbn', 'published_date', 'description',
            'row_number', 'rack_position'
        ]


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['author'].queryset = Author.objects.all()
        self.fields['department'].queryset = Department.objects.all()


class PastPaperForm(forms.ModelForm):
    new_department_name = forms.CharField(
        max_length=100,
        required=False,
        label="New Department Name"
    )
    new_department_code = forms.CharField(
        max_length=10,
        required=False,
        label="New Department Code"
    )
    new_department_category = forms.ChoiceField(
        choices=[('degree', 'Degree'), ('diploma', 'Diploma')],
        required=False,
        label="New Department Category"
    )

    class Meta:
        model = PastPaper
        fields = ['title', 'department', 'academic_year', 'published_year', 'pdf']

    def clean(self):
        cleaned_data = super().clean()
        dept = cleaned_data.get('department')
        new_name = cleaned_data.get('new_department_name')
        new_code = cleaned_data.get('new_department_code') or '00'
        new_category = cleaned_data.get('new_department_category') or 'degree'

        if not dept and not new_name:
            raise forms.ValidationError("You must select an existing department or enter a new one.")

        if new_name and not dept:
            # Create or get the department
            dept, created = Department.objects.get_or_create(
                name=new_name,
                defaults={'code': new_code, 'category': new_category}
            )
            cleaned_data['department'] = dept  # ✅ Set it here for validation to pass

        return cleaned_data


    def save(self, commit=True):
    # Department is already set in clean()
        return super().save(commit=commit)
