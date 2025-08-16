from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Post, Comment
from taggit.forms import TagWidget


# Custom User Creation Form
# This form extends Django's built-in UserCreationForm to include additional fields.
# It allows users to register with a username, email, first name, and last name.
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'location', 'birth_date', 'profile_picture', 'website']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell us about yourself...'}),
            'location': forms.TextInput(attrs={'placeholder': 'City, Country'}),
            'website': forms.URLInput(attrs={'placeholder': 'https://yourwebsite.com'}),
        }



# Post Form
# This form is used for creating and updating blog posts.
# It includes fields for the post title and content.
# The title has a maximum length of 200 characters.
# The content field allows for rich text input.
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your post title...',
                'maxlength': 200
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': "What's on your mind? Write your blog post content here..."
            }),
            'tags': TagWidget(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].help_text = 'Maximum 200 characters'
        self.fields['content'].help_text = 'Write your full blog post here. You can use paragraphs and formatting.'



# Comment Form
# This form is used for creating and updating comments on blog posts.
# It includes a single field for the comment content.
class CommentForm(forms.ModelForm):
    """Form for creating and updating comments"""
    
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your thoughts...',
                'maxlength': '1000'
            }),
        }
        labels = {
            'content': 'Comment',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({
            'id': 'comment-content',
            'data-toggle': 'tooltip',
            'title': 'Maximum 1000 characters allowed'
        })

    def clean_content(self):
        """Clean and validate comment content"""
        content = self.cleaned_data['content']
        
        # Remove leading/trailing whitespace
        content = content.strip()
        
        # Check if content is not empty after stripping
        if not content:
            raise ValidationError("Comment cannot be empty.")
        
        # Check minimum length
        if len(content) < 5:
            raise ValidationError("Comment must be at least 5 characters long.")
        
        # Sanitize HTML content to prevent XSS attacks
        allowed_tags = ['b', 'i', 'u', 'em', 'strong', 'p', 'br']
        content = bleach.clean(content, tags=allowed_tags, strip=True)
        
        return content

    def save(self, commit=True):
        """Override save to ensure proper handling"""
        comment = super().save(commit=False)
        if commit:
            comment.save()
        return comment


class CommentEditForm(CommentForm):
    """Specialized form for editing comments with additional context"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].help_text = "Edit your comment. Last updated will be recorded."
        self.fields['content'].widget.attrs.update({
            'placeholder': 'Update your thoughts...'
        })


class CommentDeleteForm(forms.Form):
    """Simple confirmation form for deleting comments"""
    confirm = forms.BooleanField(
        required=True,
        widget=forms.HiddenInput(),
        initial=True
    )

    def __init__(self, *args, **kwargs):
        self.comment = kwargs.pop('comment', None)
        super().__init__(*args, **kwargs)

    def clean_confirm(self):
        if not self.cleaned_data.get('confirm'):
            raise ValidationError("Confirmation required to delete comment.")