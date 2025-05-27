from django import forms
from apps.pages.models import Book,Suggestion,Author,Department


class AddUserForm(forms.Form):
    username = forms.CharField(max_length=30, label='Registration Number')
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(
        choices=[('student', 'Student'), ('librarian', 'Librarian'), ('admin', 'Admin')],
        required=True
    )
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=False)