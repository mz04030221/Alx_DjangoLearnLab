# relationship_app/urls.py
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView
from .views import LibraryDetailView
from .views import list_books
from django.urls import path
from django.urls import path
from .import views


urlpatterns = [
     # Authentication URLs
    path('login/', LoginView.as_view(template_name='relationship_app/login.html'), name='login'),
    path('logout/', LogoutView.as_view(template_name='relationship_app/logout.html'), name='logout'),
    path('register/', views.register, name='register'),

    # Function-based view for listing all books
    path('books/', views.list_books, name='list_books'),
    
    # Class-based view for library detail
    path('library/<int:pk>/', LibraryDetailView.as_view(), name='library_detail'),

    # Book management URLs 
    path('add_book/', views.add_book, name='add_book'),
    path('edit_book/', views.edit_book, name='edit_book'),
    path('books/<int:book_id>/delete/', views.delete_book, name='delete_book'),
    
    # Home and main pages
    path('', views.home_view, name='home'),
    
    # Role-based views 
    path('admin/', views.admin_view, name='admin_view'),
    path('librarian/', views.librarian_view, name='librarian_view'),
    path('member/', views.member_view, name='member_view'),
    
    # Access control
    path('access_denied/', views.access_denied, name='access_denied'),
    

]