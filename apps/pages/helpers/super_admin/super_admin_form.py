from django import forms
from apps.pages.models import Book,Suggestion,Author,Department

class AddUserForm(forms.Form):
    username = forms.CharField(max_length=30, label='Registration Number')
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(
        choices=[
            ('degree_student', 'Degree Student'),
            ('diploma_student', 'Diploma Student'),
            ('librarian', 'Librarian'),
            ('admin', 'Admin'),
        ],
        required=True
    )
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=False)
    phone_number = forms.CharField(max_length=15, required=True, label="Phone Number")
    new_department = forms.CharField(max_length=100, required=False, label="New Department")
