from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm

def index(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')  # Use your desired post-login redirect
            else:
                form.add_error(None, "Invalid username or password.")  # Generic error
        else:
            form.add_error(None, "Invalid username or password.")  # Validation failed

    return render(request, 'auth/login.html', {'form': form})
