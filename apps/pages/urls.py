from django.urls import path
from . import super_admin, student, views

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
    path('suggestions/', views.suggestion_page, name='suggestion_page'),
    path('view-suggestions/', views.view_suggestions, name='view_suggestions'),

    # super admin routes:
    path('add-user-page', super_admin.add_user_page, name='add_user_page'),
    path('super_admin/view-users/', super_admin.view_all_users, name='view_all_users'),

    # books
    path('books/<int:book_id>/toggle-status/', views.toggle_status, name='toggle_status'),
    path('books/<int:book_id>/delete/', views.delete_book, name='delete_book'),
    path('books/<int:book_id>/render/', views.render_book, name='render_book'),
    path('books/<int:book_id>/set_available/', views.set_book_available, name='set_book_available'),
    path('get-student-info/', views.get_student_info, name='get_student_info'),

    # student
    path('student/borrowed-books', student.get_borrowed_books, name='get_borrowed_books'),
]
