from django.urls import path

from . import views
from . import super_admin

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


    #super admin routes:
     path('add-user-page', super_admin.add_user_page, name='add_user_page'),
      path('super_admin/view-users/', super_admin.view_all_users, name='view_all_users')
     

]
