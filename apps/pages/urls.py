from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.index, name='login'),
    path('student/home', views.student_home, name='student_home'),
    path('librarian/home', views.librarian_home, name='librarian_home'),
    path('home', views.home, name='home'),
]
