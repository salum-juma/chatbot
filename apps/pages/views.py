import json
from django.shortcuts import render,redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.contrib import messages
from django.http import HttpResponse
from  apps.pages.helpers.library.forms import BookForm,SuggestionForm
from .models import Book,Suggestion,Author,Department,Student,User
from django.db.models import Q
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponseNotAllowed

def get_student_info(request):
    reg_number = request.GET.get('reg_number')
    try:
        student = Student.objects.get(reg_number=reg_number)
        return JsonResponse({
            'name': student.name,
            'department': student.department
        })
    except Student.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)

    



@csrf_exempt
def index(request):
    if request.method == 'POST':
        try:
            # Parse JSON data
            data = json.loads(request.body)
            registration_no = data.get('registration')
            password = data.get('password')
            to_json = data.get('toJson', False)

            user = authenticate(request, username=registration_no, password=password)

            if user is not None:
                login(request, user)

                if to_json:
                    return JsonResponse({
                        'status': 'success',
                        'role': user.role,
                        'message': f"Logged in as {user.role}",
                    })

                # Normal role-based response
                if user.role == 'admin':
                    return redirect('add_user_page')
                elif user.role == 'student':
                    return HttpResponse("student")
                elif user.role == 'librarian':
                    return HttpResponse("librarian")
                else:
                    return HttpResponse("default")
            else:
                return JsonResponse({'status': 'false', 'message': 'Invalid credentials'}, status=401)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format'}, status=400)
    else:
        return render(request, 'auth/login.html')

    


def home(request):
    user = request.user
    if user.role == 'librarian':
          return redirect('librarian/home')
        
    elif user.role == 'student':
        return render(request, 'student/home.html', {'name': user.full_name})
    
    elif user.role == 'admin':
        return redirect( 'add_user_page')
    else:
        return HttpResponse(f"You are logged in as a {user.role}.")



def student_home(request):
    return render(request, 'student/home.html')



def suggestion_page(request):
    if request.method == 'POST':
        form = SuggestionForm(request.POST)
        if form.is_valid():
            suggestion = form.save(commit=False)
            if request.user.is_authenticated:
                suggestion.user = request.user  
            suggestion.save()
            messages.success(request, 'Thank you for your suggestion!')
            return redirect('suggestion_page')
    else:
        form = SuggestionForm()
    return render(request, 'common/suggestion_form.html', {'form': form})

def view_suggestions(request):
    suggestions = Suggestion.objects.all()
    return render(request, 'common/view_suggestions.html', {'suggestions': suggestions})





def custom_logout(request):
    logout(request)  
    return HttpResponseRedirect('/login/') 