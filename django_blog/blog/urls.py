from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


# Home and Authentication URLs
# This file defines the URL patterns for the blog application.
# It includes paths for the home page, user registration, user profile,
# viewing a specific user's profile, and login/logout functionality.
# The login path uses a custom template for the login view.
# The urlpatterns list routes URLs to views.
urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('profile/<str:username>/', views.profile_view, name='profile_view'),
    path('login/', auth_views.LoginView.as_view(template_name='blog/login.html'), name='blog/login'), # custom login template
    path('logout/', views.custom_logout, name='logout'),


    # Blog Post CRUD URLs
    path('posts/', views.PostListView.as_view(), name='post-list'),
    path('post/new/', views.PostCreateView.as_view(), name='post-create'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),
    path('post/<int:pk>/update/', views.PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post-delete'),


    # Comment-related URLs
    path('post/<int:pk>/comments/new/', views.CommentCreateView.as_view(), name='comment_create'),
    path('comment/<int:pk>/update/', views.CommentUpdateView.as_view(), name='comment_update'),
    path('comment/<int:pk>/delete/', views.CommentDeleteView.as_view(), name='comment_delete'),

    # AJAX endpoint for comments (optional)
    path('post/<slug:slug>/comment/ajax/', 
         views.comment_ajax_create, 
         name='comment_ajax_create'),
    
    # User comments page
    path('user/<str:username>/comments/', 
         views.user_comments, 
         name='user_comments'),

    # Search and Tag URLs
    path('search/', views.search_posts, name='search_posts'),
    path('tags/<slug:tag_slug>/', views.posts_by_tag, name='posts_by_tag'),
    path('tags/<slug:tag_slug>/', views.PostByTagListView.as_view(), name='posts_by_tag'),
]
