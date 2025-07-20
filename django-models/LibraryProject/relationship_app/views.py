from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import DetailView
from django.http import HttpResponse, HttpResponseForbidden
from .models import Book, Library, UserProfile
from django.core.exceptions import PermissionDenied


def is_admin(user):
    """
    Check if the user has Admin role.
    """
    if not user.is_authenticated:
        return False
    try:
        return user.userprofile.role == "Admin"
    except UserProfile.DoesNotExist:
        return False


def is_librarian(user):
    """
    Check if the user has Librarian role.
    """
    if not user.is_authenticated:
        return False
    try:
        return user.userprofile.role == "Librarian"
    except UserProfile.DoesNotExist:
        return False


def is_member(user):
    """
    Check if the user has Member role.
    """
    if not user.is_authenticated:
        return False
    try:
        return user.userprofile.role == "Member"
    except UserProfile.DoesNotExist:
        return False


@login_required
def admin_view(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.role == "Admin":
            return render(
                request, "relationship_app/admin_home.html"
            )  # this template must exist
        else:
            return HttpResponseForbidden("You are not authorized to view this page.")
    except UserProfile.DoesNotExist:
        return HttpResponseForbidden("User profile not found.")


@login_required
@user_passes_test(is_librarian, login_url="/access_denied/")
def librarian_view(request):
    """
    View accessible only to users with Librarian role.
    """
    context = {
        "user_role": request.user.userprofile.role,
        "page_title": "Librarian Dashboard",
        "welcome_message": f"Welcome, {request.user.username}! You have librarian access.",
    }
    return render(request, "librarian_view.html", context)


@login_required
@user_passes_test(is_member, login_url="/access_denied/")
def member_view(request):
    """
    View accessible only to users with Member role.
    """
    context = {
        "user_role": request.user.userprofile.role,
        "page_title": "Member Dashboard",
        "welcome_message": f"Welcome, {request.user.username}! You have member access.",
    }
    return render(request, "member_view.html", context)


def access_denied(request):
    """
    View to handle access denied scenarios.
    """
    context = {
        "message": "Access Denied: You do not have permission to view this page.",
    }
    return render(request, "access_denied.html", context, status=403)


# Registration view
def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("library_list")
    else:
        form = UserCreationForm()
    return render(request, "relationship_app/register.html", {"form": form})


# Book list
def list_books(request):
    books = Book.objects.all()
    return render(request, "relationship_app/list_books.html", {"books": books})


# Library detail view
class LibraryDetailView(DetailView):
    model = Library
    template_name = "relationship_app/library_detail.html"
    context_object_name = "library"


# "from .models import Library"
# "from django.views.generic.detail import DetailView"
# "from django.contrib.auth.decorators import permission_required", "relationship_app.can_add_book", "relationship_app.can_change_book", "relationship_app.can_delete_book"
# @user_passes_test
