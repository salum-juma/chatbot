from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.index, name='login'),
    path('student/home', views.student_home, name='student_home'),
    path('librarian/home', views.librarian_home, name='librarian_home'),
    path('librarian/add-book', views.add_book, name='add_book'),
    path('student/search-books/', views.search_books, name='search_books'),
    path('view-books/', views.view_books, name='view_books'),
    path('home', views.home, name='home'),
    path('logout/', views.custom_logout, name='logout'),
]
