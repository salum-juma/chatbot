import json
from django.shortcuts import render,redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.http import HttpResponse
from huggingface_hub import logout
from  apps.pages.helpers.library.forms import BookForm,SuggestionForm
from apps.pages.whatsapp.utils.sms_logic import send_sms
from .models import Book,Suggestion,Author,Department,Student,User
from django.db.models import Q
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponseNotAllowed
import random
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User, OTPStorage 
from django.contrib.messages import get_messages

import random
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User, OTPStorage

def forgot_password(request):
    if request.method == "POST":
        reg_no = request.POST.get('registration_no')
        try:
            user = User.objects.get(registration_no=reg_no)
        except User.DoesNotExist:
            messages.error(request, "User not found")
            return redirect('forgot_password')

        # Generate a 4-digit OTP
        otp = str(random.randint(1000, 9999))

        # Store OTP in database (you might want to clear old ones first)
        OTPStorage.objects.create(user=user, otp_code=otp)

        # Prepare and send OTP via SMS
        sms_message = f"Your OTP for password reset is: {otp}. Do not share this code with anyone."
        sms_sent = send_sms(user.phone_number, sms_message)

        if sms_sent:
            messages.success(request, "OTP sent to your registered phone number.")
        else:
            messages.warning(request, "OTP generated, but failed to send SMS.")

        # Save reg_no in session for use in verification
        request.session['reset_reg_no'] = reg_no

        return redirect('verify_otp')

    return render(request, 'auth/forgot_password.html')



def verify_otp(request):
    reg_no = request.session.get('reset_reg_no')
    if not reg_no:
        return redirect('forgot_password')

    user = User.objects.get(registration_no=reg_no)

    if request.method == "POST":
        otp = ''.join([
            request.POST.get('otp1', ''),
            request.POST.get('otp2', ''),
            request.POST.get('otp3', ''),
            request.POST.get('otp4', ''),
        ])

        otp_records = OTPStorage.objects.filter(user=user, otp_code=otp).order_by('-created_at')
        if not otp_records.exists() or not otp_records.first().is_valid():
            messages.error(request, "Invalid or expired OTP.")
            return redirect('verify_otp')

        # Mark user as OTP verified
        request.session['otp_verified'] = True
        return redirect('reset_password')

    return render(request, 'auth/verify_otp.html')

def reset_password(request):
    if not request.session.get('otp_verified'):
        return redirect('verify_otp')

    reg_no = request.session.get('reset_reg_no')
    user = User.objects.get(registration_no=reg_no)

    if request.method == 'POST':
        password = request.POST.get('new_password')
        confirm = request.POST.get('confirm_password')

        if password != confirm:
            messages.error(request, "Passwords do not match.")
            return redirect('reset_password')

        user.set_password(password)
        user.save()
        messages.success(request, "Password reset successfully.")
        request.session.pop('reset_reg_no', None)
        request.session.pop('otp_verified', None)
        return redirect('login')

    return render(request, 'auth/reset_password.html')


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
        # Clear lingering messages (e.g. announcement success messages)
        list(get_messages(request))  # This clears any previously stored messages

        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                registration_no = data.get('registration')
                password = data.get('password')
                to_json = data.get('toJson', False)
            except json.JSONDecodeError:
                return JsonResponse({'status': 'error', 'message': 'Invalid JSON format'}, status=400)
        else:
            registration_no = request.POST.get('username')
            password = request.POST.get('password')
            to_json = False

        user = authenticate(request, username=registration_no, password=password)

        if user:
            login(request, user)
            if to_json:
                return JsonResponse({
                    'status': 'success',
                    'role': user.role,
                    'message': f"Logged in as {user.role}",
                })

            # HTML form fallback
            if user.role == 'admin':
                return redirect('add_user_page')
            elif user.role == 'student':
                return redirect('student_home')
            elif user.role == 'librarian':
                return redirect('librarian_home')
            elif user.role == 'canteen':
                return redirect('menu_page')
            else:
                return HttpResponse("Unknown role")
        else:
            if to_json:
                return JsonResponse({'status': 'false', 'message': 'Invalid credentials'}, status=401)
            return render(request, 'auth/login.html', {'error': 'Invalid credentials'})

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
    return HttpResponseRedirect('/login-user/') 