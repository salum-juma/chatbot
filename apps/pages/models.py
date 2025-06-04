from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# User model
class UserManager(BaseUserManager):
    def create_user(self, registration_no, password=None, **extra_fields):
        if not registration_no:
            raise ValueError("The registration number is required")
        user = self.model(registration_no=registration_no, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, registration_no, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(registration_no, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('librarian', 'Librarian'),
        ('admin', 'Admin'),
    )

    registration_no = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'registration_no'
    REQUIRED_FIELDS = ['email', 'full_name']

    def __str__(self):
        return f"{self.registration_no} ({self.role})"

# Student model
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    enrollment_year = models.PositiveIntegerField()
    program = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, blank=True)
    gender = models.CharField(max_length=10, choices=[("Male", "Male"), ("Female", "Female")], blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    reg_number = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100,default='Sample')
    department =  models.CharField(max_length=100, default='General')

    def __str__(self):
        return f"{self.user.full_name} ({self.user.registration_no})"

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Author(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name
        
class Book(models.Model):
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Rendered', 'Rendered'),
    ]
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    isbn = models.CharField(max_length=13)
    published_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    row_number = models.CharField(max_length=50, blank=True, null=True)  # newly added
    rack_position = models.CharField(max_length=50, blank=True, null=True)  # newly added
    status = models.CharField(max_length=20, choices=[('Available', 'Available'), ('Rendered', 'Rendered')], default='Available')
    rendered_to = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True)
    render_from = models.DateField(null=True, blank=True)
    render_to = models.DateField(null=True, blank=True)
    def __str__(self):
        return self.title




class Suggestion(models.Model):
    SUGGESTION_TYPES = [
        ('feature', 'Feature Request'),
        ('bug', 'Bug Report'),
        ('general', 'General Feedback'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='suggestions')
    suggestion_type = models.CharField(max_length=20, choices=SUGGESTION_TYPES, default='general')
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_reviewed = models.BooleanField(default=False)

    def __str__(self):
        return f"Suggestion #{self.id} ({self.get_suggestion_type_display()})"


class Penalty(models.Model):
    STATUS_CHOICES = [
        ('Unpaid', 'Unpaid'),
        ('Paid', 'Paid'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    days_late = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Unpaid')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.book} - {self.status}"

class ChatSession(models.Model):
    phone_number = models.CharField(max_length=20, unique=True)
    stage = models.CharField(max_length=50, default='initial')  # Track conversation stage
    reg_number = models.CharField(max_length=50, blank=True, null=True)
    password = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.phone_number

# Create your models here.

class Product(models.Model):
    id    = models.AutoField(primary_key=True)
    name  = models.CharField(max_length = 100) 
    info  = models.CharField(max_length = 100, default = '')
    price = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name
