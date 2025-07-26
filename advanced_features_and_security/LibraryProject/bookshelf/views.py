from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from .models import Book
from .forms import BookForm


# Book List View - Requires can_view permission
@login_required
@permission_required("bookshelf.can_view", raise_exception=True)
def book_list(request):
    """
    Display list of all books. Requires 'can_view' permission.
    """
    books = Book.objects.all()
    return render(request, "bookshelf/book_list.html", {"books": books})


# Book Detail View - Requires can_view permission
@login_required
@permission_required("bookshelf.can_view", raise_exception=True)
def book_detail(request, book_id):
    """
    Display details of a specific book. Requires 'can_view' permission.
    """
    book = get_object_or_404(Book, id=book_id)
    return render(request, "bookshelf/book_detail.html", {"book": book})


# Book Create View - Requires can_create permission
@login_required
@permission_required("bookshelf.can_create", raise_exception=True)
def book_create(request):
    """
    Create a new book. Requires 'can_create' permission.
    """
    if request.method == "POST":
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Book created successfully!")
            return redirect("book_list")
    else:
        form = BookForm()
    return render(
        request,
        "bookshelf/book_form.html",
        {"form": form, "title": "Create Book", "action": "Create"},
    )


# Book Edit View - Requires can_edit permission
@login_required
@permission_required("bookshelf.can_edit", raise_exception=True)
def book_edit(request, book_id):
    """
    Edit an existing book. Requires 'can_edit' permission.
    """
    book = get_object_or_404(Book, id=book_id)
    if request.method == "POST":
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, "Book updated successfully!")
            return redirect("book_detail", book_id=book.id)
    else:
        form = BookForm(instance=book)
    return render(
        request,
        "bookshelf/book_form.html",
        {"form": form, "title": "Edit Book", "action": "Update", "book": book},
    )


# Book Delete View - Requires can_delete permission
@login_required
@permission_required("bookshelf.can_delete", raise_exception=True)
def book_delete(request, book_id):
    """
    Delete a book. Requires 'can_delete' permission.
    """
    book = get_object_or_404(Book, id=book_id)
    if request.method == "POST":
        book.delete()
        messages.success(request, "Book deleted successfully!")
        return redirect("book_list")
    return render(request, "bookshelf/book_confirm_delete.html", {"book": book})


# Helper view to check user permissions (for testing)
@login_required
def user_permissions(request):
    """
    Display current user's permissions for testing purposes.
    """
    user = request.user
    permissions = {
        "can_view": user.has_perm("bookshelf.can_view"),
        "can_create": user.has_perm("bookshelf.can_create"),
        "can_edit": user.has_perm("bookshelf.can_edit"),
        "can_delete": user.has_perm("bookshelf.can_delete"),
    }
    return render(
        request,
        "bookshelf/user_permissions.html",
        {"user": user, "permissions": permissions},
    )


# "from .forms import ExampleForm"

