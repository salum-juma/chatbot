from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from datetime import timedelta

# -------------------------
# Custom User Management
# -------------------------

class OTPStorage(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return timezone.now() < self.created_at + timedelta(minutes=5)

    def __str__(self):
        return f"OTP for {self.user.registration_no} - {self.otp_code}"


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
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'registration_no'
    REQUIRED_FIELDS = ['email', 'full_name']

    def __str__(self):
        return f"{self.registration_no} ({self.role})"


class Guideline(models.Model):
    title = models.CharField(max_length=255)
    name = models.TextField()  # Content or description of the guideline

# -------------------------
# Department
# -------------------------

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, default='00')
    category = models.CharField(
        max_length=20,
        choices=[('degree', 'Degree'), ('diploma', 'Diploma')],
        default='degree'
    )

    def __str__(self):
        return f"{self.name} ({self.category})"


# -------------------------
# Student Profile
# -------------------------

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    reg_number = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100, default='Sample')
    enrollment_year = models.PositiveIntegerField()
    program = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, blank=True)
    gender = models.CharField(max_length=10, choices=[("Male", "Male"), ("Female", "Female")], blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    department = models.CharField(max_length=100, default='General')

    year = models.ForeignKey('Year', on_delete=models.SET_NULL, null=True, blank=True, related_name='students')

    def __str__(self):
        return f"{self.user.full_name} ({self.reg_number})"


# -------------------------
# Library System
# -------------------------

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
    row_number = models.CharField(max_length=50, blank=True, null=True)
    rack_position = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')
    rendered_to = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True)
    render_from = models.DateField(null=True, blank=True)
    render_to = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title

    @property
    def shelf_location(self):
        if self.row_number and self.rack_position:
            return f"Row {self.row_number}, Rack {self.rack_position}"
        return "Not available"


# -------------------------
# Penalty System
# -------------------------

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


# -------------------------
# Suggestion & Feedback
# -------------------------

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


# -------------------------
# Chat Session for Bot
# -------------------------

class ChatSession(models.Model):
    phone_number = models.CharField(max_length=20, unique=True)
    stage = models.CharField(max_length=50, default='initial')
    reg_number = models.CharField(max_length=50, blank=True, null=True)
    password = models.CharField(max_length=100, blank=True, null=True)
    last_message_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    data = models.JSONField(default=dict, blank=True)
    temp_meal_id = models.CharField(max_length=50, null=True, blank=True)
    temp_data = models.JSONField(null=True, blank=True)
    temp_order_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.phone_number


# -------------------------
# Past Papers
# -------------------------

class PastPaper(models.Model):
    YEAR_CHOICES = [
        (1, '1st Year'),
        (2, '2nd Year'),
        (3, '3rd Year'),
        (4, '4th Year'),
    ]

    title = models.CharField(max_length=255)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    academic_year = models.PositiveSmallIntegerField(choices=YEAR_CHOICES)
    published_year = models.PositiveIntegerField()
    pdf = models.FileField(upload_to='past_papers/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.published_year})"


# -------------------------
# Announcements
# -------------------------

class AnnouncementCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Announcement(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    category = models.ForeignKey(AnnouncementCategory, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    first_year_only = models.BooleanField(default=False)  # ✅ NEW FIELD

    def __str__(self):
        return self.title


class MenuItem(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='subitems',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name

class MealOrder(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('verified', 'Verified'),
    ]
        
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    ordered_at = models.DateTimeField(default=timezone.now)
    total_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    token = models.CharField(max_length=10, blank=True, null=True)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role': 'librarian'})
    verified_at = models.DateTimeField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    transaction_message = models.TextField(null=True, blank=True)
    phone_number_id = models.CharField(max_length=50, blank=True, null=True)
 

    def __str__(self):
        return f"{self.student.reg_number} - {self.status} - {self.ordered_at.strftime('%Y-%m-%d %H:%M')}"


class MealOrderItem(models.Model):
    order = models.ForeignKey(MealOrder, related_name='items', on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.menu_item.name} x {self.quantity}"
    

class Year(models.Model):
    number = models.PositiveSmallIntegerField(unique=True)
    label = models.CharField(max_length=20)

    def __str__(self):
        return self.label

 
# -------------------------
# Cafeteria Products
# -------------------------

class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    info = models.CharField(max_length=100, default='', blank=True)
    price = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name
