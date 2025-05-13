from django.shortcuts import render
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import HttpResponse

def index(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)

                # Check the role and return the response text accordingly
                if user.role == 'student':
                    return HttpResponse("student")  # Return "student" as text
                elif user.role == 'librarian':
                    return HttpResponse("librarian")  # Return "librarian" as text
                else:
                    return HttpResponse("default")  # Return "default" or other role
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'auth/login.html', {'form': form})



def home(request):
    user = request.user
    return HttpResponse(f"You are logged in as a {user.role}.")



def student_home(request):
    return render(request, 'student/home.html')


def librarian_home(request):
    return render(request, 'librarian/home.html')
