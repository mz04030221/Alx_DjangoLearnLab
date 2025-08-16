Django Blog Authentication System Documentation
Overview
The Django Blog authentication system provides comprehensive user management functionality including registration, login, logout, and profile management. The system leverages Django's built-in authentication framework while extending it with custom forms and profile features.

System Architecture
1. Models
User Model (Built-in Django)

Purpose: Handles basic user authentication data
Fields: username, email, password, first_name, last_name, date_joined
Location: Django's built-in django.contrib.auth.models.User

Profile Model (Custom Extension)

Purpose: Extends user data with additional profile information
Location: blog/models.py
Fields:

user: OneToOneField linking to User model
bio: TextField for user biography (max 500 characters)
location: CharField for user location
birth_date: DateField for birth date
profile_picture: ImageField for profile photos
website: URLField for personal website



Automatic Profile Creation: When a new user registers, a Profile is automatically created using Django signals (post_save).
2. Forms
CustomUserCreationForm

Purpose: Handles user registration with extended fields
Location: blog/forms.py
Features:

Extends Django's UserCreationForm
Adds email, first_name, last_name fields
Email validation and requirement
Custom save method to handle additional fields



UserUpdateForm

Purpose: Handles basic user information updates
Fields: username, first_name, last_name, email
Validation: Email format validation, username uniqueness

ProfileUpdateForm

Purpose: Handles profile-specific information updates
Features:

File upload for profile pictures
Date picker widget for birth_date
URL validation for website field
Textarea with placeholder for bio



3. Views
Authentication Views
register(request)

Purpose: Handles user registration
Methods: GET (display form), POST (process registration)
Process:

Display registration form on GET
Validate form data on POST
Create new user account
Display success message
Redirect to login page


Template: blog/register.html

LoginView (Django Built-in)

Purpose: Handles user login
Configuration: Uses Django's django.contrib.auth.views.LoginView
Template: registration/login.html
Redirects: To home page on successful login (LOGIN_REDIRECT_URL = '/')

custom_logout(request)

Purpose: Handles user logout with custom messaging
Process:

Log out current user
Display success message
Render logout confirmation page


Template: registration/logged_out.html

Profile Management Views
profile(request)

Purpose: User profile editing (authenticated users only)
Decorator: @login_required
Methods: GET (display forms), POST (update profile)
Process:

Load current user and profile data
Display update forms
Validate and save changes on POST
Handle both User and Profile model updates


Template: blog/profile.html

profile_view(request, username)

Purpose: Public profile viewing
Process:

Look up user by username
Display profile information and posts
Show edit link if viewing own profile


Template: blog/profile_view.html

================

# Django Blog Application

## Overview

This Django Blog application allows users to create, view, edit, and delete blog posts. It features user authentication, user profiles with profile pictures, and a clean, user-friendly interface.

---

## Features

### Blog Posts (CRUD)
- **Create:** Authenticated users can create new blog posts with a title and content.
- **Read:** 
  - All users can view a list of all blog posts, ordered by newest first.
  - Each post has a detail page showing the full content.
- **Update:** Only the author of a post can edit their post.
- **Delete:** Only the author of a post can delete their post.

### User Authentication
- User registration, login, and logout.
- Only logged-in users can create, edit, or delete posts.

### User Profiles
- Each user has a profile with:
  - Bio
  - Location
  - Birth date
  - Website
  - Profile picture (with automatic resizing and a default image if none is uploaded)
- Profiles are created automatically when a user registers.

### Templates
- Responsive and user-friendly HTML templates for:
  - Listing all posts
  - Viewing post details
  - Creating and editing posts
  - Deleting posts (confirmation)
  - User registration, login, and profile pages

### Other Features
- Success messages for create, update, and delete actions.
- Pagination for the post list.
- Secure: Only authors can modify or delete their own posts.

---

## File Structure

```
blog/
├── templates/
│   └── blog/
│       ├── base.html
│       ├── post_list.html
│       ├── post_detail.html
│       ├── post_form.html
│       ├── post_confirm_delete.html
│       ├── register.html
│       ├── profile.html
│       └── login.html
├── models.py
├── views.py
├── forms.py
├── urls.py
```

---

## Getting Started

1. **Clone the repository and install dependencies:**
    ```sh
    git clone <repo-url>
    cd django_blog
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

2. **Apply migrations:**
    ```sh
    python manage.py makemigrations
    python manage.py migrate
    ```

3. **Create a superuser (optional, for admin access):**
    ```sh
    python manage.py createsuperuser
    ```

4. **Run the development server:**
    ```sh
    python manage.py runserver
    ```

5. **Access the app:**
    - Visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

---

## Notes

- Make sure to add a `default.jpg` image in `media/profile_pics/` for default profile pictures.
- Static files (CSS, JS) should be placed in the `static/` directory.
- For production, configure `DEBUG`, `ALLOWED_HOSTS`, and static/media file serving appropriately.

---

## License
===========
