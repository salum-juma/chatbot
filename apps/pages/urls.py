from django.shortcuts import redirect
from django.urls import path

from apps.pages import canteen
from . import super_admin, student, views, librarian,chatbot
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('login-user/', views.index, name='login-user'),
    path('logout-user/', views.custom_logout, name='logout-user'),
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
    path('librarian/get-student-info/', views.get_student_info, name='get_student_info'),
    path('librarian/penalties/', librarian.view_penalties, name='view_penalties'),

    path('past-papers/', librarian.past_papers, name='past_paper_list'),
    path('past-papers/add/', librarian.add_past_paper, name='add_past_paper'),
    path('past-papers/delete/<int:pk>/', librarian.delete_past_paper, name='delete_past_paper'),
    

    # Suggestions
    path('suggestions/', views.suggestion_page, name='suggestion_page'),
    path('view-suggestions/', views.view_suggestions, name='view_suggestions'),

    # Super admin routes
    path('add-user-page', super_admin.add_user_page, name='add_user_page'),
    path('super_admin/view-users/', super_admin.view_all_users, name='view_all_users'),
    path('announcements/', super_admin.announcements_page, name='announcements'),
    path('announcements/add/', super_admin.add_announcement, name='add_announcement'),
    path('announcements/delete/<int:ann_id>/', super_admin.delete_announcement, name='delete_announcement'),
    path('dummy-users/', super_admin.add_dummy_users, name='dummy_users'),

    # whatsapp
    path('webhook/', chatbot.whatsapp_webhook, name='whatsapp_webhook'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('reset-password/', views.reset_password, name='reset_password'),


    # canteen
    path('canteen/home', canteen.canteen_home, name='canteen_home'),
    path('canteen/menu/', canteen.menu_page, name='menu_page'),
    path('canteen/menu/add/', canteen.add_menu_item, name='add_menu_item'),
    path('canteen/menu-item/delete/<int:pk>/', canteen.delete_menu_item, name='delete_menu_item'),

        ]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
