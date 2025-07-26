# relationship_app/views.py
from django.views.generic.detail import DetailView
from django.shortcuts import render
from django.views.generic import ListView
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, HttpResponseForbidden
from django.core.exceptions import PermissionDenied
from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from .models import Library
from .models import Book
from .models import Author
from .models import UserProfile
from .forms import BookForm


# Function-based view to list all books
def list_books(request):
    """
    Function-based view that lists all books with their authors.
    """
    books = Book.objects.all()
    return render(request, 'relationship_app/list_books.html', {'books': books})


# Class-based view for library details 
class LibraryDetailView(DetailView):
    """Create a class-based view that displays details for a specific library, listing all books available in that library."""
    model = Library
    template_name = 'relationship_app/library_detail.html'
    context_object_name = 'library'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['books'] = self.object.books.all()  
        return context




def is_admin(user):
    """
    User Admin role.
    """
    if not user.is_authenticated:
        return False
    try:
        return user.userprofile.role == 'Admin'
    except UserProfile.DoesNotExist:
        return False


def is_librarian(user):
    """
   User Librarian role.
    """
    if not user.is_authenticated:
        return False
    try:
        return user.userprofile.role == 'Librarian'
    except UserProfile.DoesNotExist:
        return False


def is_member(user):
    """
    user has Member role.
    """
    if not user.is_authenticated:
        return False
    try:
        return user.userprofile.role == 'Member'
    except UserProfile.DoesNotExist:
        return False


# Home view that redirects based on user role
@login_required
def home_view(request):
    """
    Home view that redirects users based on their role.
    """
    if hasattr(request.user, 'userprofile'):
        role = request.user.userprofile.role
        if role == 'Admin':
            return redirect('admin_view')
        elif role == 'Librarian':
            return redirect('librarian_view')
        elif role == 'Member':
            return redirect('member_view')
    
    return render(request, 'relationship_app/home.html')


@login_required
@user_passes_test(is_admin, login_url='/access_denied/')
def admin_view(request):
    """
    View accessible only to users with Admin role.
    """
    context = {
        'user_role': request.user.userprofile.role,
        'page_title': 'Admin Dashboard',
        'welcome_message': f'Welcome, {request.user.username}! You have admin access.',
    }
    return render(request, 'relationship_app/admin_view.html', context)


@login_required
@user_passes_test(is_librarian, login_url='/access_denied/')
def librarian_view(request):
    """
    View accessible only to users with Librarian role.
    """
    context = {
        'user_role': request.user.userprofile.role,
        'page_title': 'Librarian Dashboard',
        'welcome_message': f'Welcome, {request.user.username}! You have librarian access.',
    }
    return render(request, 'relationship_app/librarian_view.html', context)


@login_required
@user_passes_test(is_member, login_url='/access_denied/')
def member_view(request):
    """
    View accessible only to users with Member role.
    """
    context = {
        'user_role': request.user.userprofile.role,
        'page_title': 'Member Dashboard',
        'welcome_message': f'Welcome, {request.user.username}! You have member access.',
    }
    return render(request, 'relationship_app/member_view.html', context)


def access_denied(request):
    """
    View to handle access denied scenarios.
    """
    context = {
        'message': 'Access Denied: You do not have permission to view this page.',
    }
    return render(request, 'relationship_app/access_denied.html', context, status=403)


# Registration view
def register(request):
    """
    User registration view.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create a default UserProfile with Member role
            UserProfile.objects.create(user=user, role='Member')
            auth_login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'relationship_app/register.html', {'form': form})


# NEW PERMISSION-BASED VIEWS FOR TASK 4


@permission_required('relationship_app.can_add_book', raise_exception=True)
def add_book(request):
    """
    View to add a new book - requires can_add_book permission
    """
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book added successfully!')
            return redirect('list_books')
    else:
        form = BookForm()
    return render(request, 'relationship_app/add_book.html', {'form': form})


@permission_required('relationship_app.can_change_book', raise_exception=True)
def edit_book(request, book_id):
    """
    View to edit an existing book - requires can_change_book permission
    """
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book updated successfully!')
            return redirect('list_books')
    else:
        form = BookForm(instance=book)
    return render(request, 'relationship_app/edit_book.html', {'form': form, 'book': book})


@permission_required('relationship_app.can_delete_book', raise_exception=True)
def delete_book(request, book_id):
    """
    View to delete a book - requires can_delete_book permission
    """
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Book deleted successfully!')
        return redirect('list_books')
    return render(request, 'relationship_app/delete_book.html', {'book': book})