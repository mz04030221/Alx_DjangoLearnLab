from django.urls import path
from . import views

urlpatterns = [
    # Book CRUD operations with permission checks
    path('', views.book_list, name='book_list'),
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),
    path('book/create/', views.book_create, name='book_create'),
    path('book/<int:book_id>/edit/', views.book_edit, name='book_edit'),
    path('book/<int:book_id>/delete/', views.book_delete, name='book_delete'),
    
    # Permission testing view
    path('permissions/', views.user_permissions, name='user_permissions'),
]
