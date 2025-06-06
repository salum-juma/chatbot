from django.urls import path
from . import super_admin, student, views, librarian,chatbot

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.index, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('home', views.home, name='home'),

    # Student routes
    path('student/home', views.student_home, name='student_home'),
    path('student/search-books/', librarian.search_books, name='search_books'),
    path('student/borrowed-books', student.get_borrowed_books, name='get_borrowed_books'),

    # Librarian routes
    path('librarian/home', librarian.librarian_home, name='librarian_home'),
    path('librarian/add-book', librarian.add_book, name='add_book'),
    path('librarian/view-books/', librarian.view_books, name='view_books'),
    path('librarian/books/<int:book_id>/toggle-status/', librarian.toggle_status, name='toggle_status'),
    path('librarian/books/<int:book_id>/delete/', librarian.delete_book, name='delete_book'),
    path('librarian/books/<int:book_id>/render/', librarian.render_book, name='render_book'),
    path('books/<int:book_id>/set_available/', librarian.set_book_available, name='set_book_available'),
    path('librarian/get-student-info/', views.get_student_info, name='get_student_info'),  # if this remains in views
    path('librarian/penalties/', librarian.view_penalties, name='view_penalties'),



    # Suggestions
    path('suggestions/', views.suggestion_page, name='suggestion_page'),
    path('view-suggestions/', views.view_suggestions, name='view_suggestions'),

    # Super admin routes
    path('add-user-page', super_admin.add_user_page, name='add_user_page'),
    path('super_admin/view-users/', super_admin.view_all_users, name='view_all_users'),


    # whatsapp
    path('webhook/', chatbot.whatsapp_webhook, name='whatsapp_webhook'),
    
        ]
