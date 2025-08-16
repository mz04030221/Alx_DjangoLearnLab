from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse 
from .forms import CustomUserCreationForm, UserUpdateForm, ProfileUpdateForm, PostForm
from .models import Post, Comment, Profile
from django.http import HttpResponseRedirect, JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .forms import CommentForm, CommentEditForm, CommentDeleteForm
from taggit.models import Tag


# PostByTagListView

class PostByTagListView(ListView):
    model = Post
    template_name = 'blog/posts_by_tag.html'
    context_object_name = 'posts'

    def get_queryset(self):
        tag_slug = self.kwargs.get('tag_slug')
        return Post.objects.filter(tags__slug=tag_slug)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.kwargs.get('tag_slug')
        return context
    
    
# authentication views
def home(request):
    posts = Post.objects.all()[:5]  # Get latest 5 posts
    return render(request, 'blog/home.html', {'posts': posts})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'blog/register.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'u_form': u_form,
        'p_form': p_form,
        'user_posts': Post.objects.filter(author=request.user)
    }
    return render(request, 'blog/profile.html', context)

def profile_view(request, username):
    """View for displaying a user's public profile"""
    user = get_object_or_404(User, username=username)
    user_posts = Post.objects.filter(author=user)
    
    context = {
        'profile_user': user,
        'user_posts': user_posts,
        'is_own_profile': request.user == user if request.user.is_authenticated else False
    }
    return render(request, 'blog/profile_view.html', context)

def custom_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully!')
    return render(request, 'registration/logged_out.html')



# Blog Post CRUD Views
class PostListView(ListView): # List all blog posts
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    ordering = ['-published_date']
    paginate_by = 5
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'All Blog Posts'
        return context

class PostDetailView(DetailView): # View a single blog post
    # This view displays the details of a single blog post.
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'

class PostCreateView(LoginRequiredMixin, CreateView): # Create a new blog post
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Your post has been created successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New Post'
        context['button_text'] = 'Create Post'
        return context

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView): # Update an existing blog post
    # This view allows the author to edit their blog post.
    # It checks if the user is the author before allowing updates.
    # If the user is not the author, they will be redirected to a 403 Forbidden page.
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    
    def form_valid(self, form):
        messages.success(self.request, 'Your post has been updated successfully!')
        return super().form_valid(form)
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Post'
        context['button_text'] = 'Update Post'
        return context

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView): # Delete a blog post
    # This view allows the author to delete their blog post.
    # It checks if the user is the author before allowing deletion.
    # If the user is not the author, they will be redirected to a 403 Forbidden page.
    # After deletion, a success message is displayed.
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    context_object_name = 'post'
    success_url = reverse_lazy('post-list')
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Your post has been deleted successfully!')
        return super().delete(request, *args, **kwargs)
    



# This view displays a blog post along with its comments.
# It allows users to view comments, post new comments, and paginate through existing comments.
def post_detail_with_comments(request, slug):
    """Enhanced post detail view with comments"""
    post = get_object_or_404(Post, slug=slug, status='published')
    
    # Get all active comments for this post
    comments = Comment.objects.filter(
        post=post, 
        is_active=True
    ).select_related('author').order_by('created_at')
    
    # Paginate comments if there are many
    paginator = Paginator(comments, 10)  # Show 10 comments per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Initialize comment form
    comment_form = CommentForm()
    
    # Handle comment form submission
    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Your comment has been posted!')
            return HttpResponseRedirect(f"{post.get_absolute_url()}#comment-{comment.id}")
        else:
            messages.error(request, 'Please correct the errors below.')
    
    context = {
        'post': post,
        'comments': page_obj,
        'comment_form': comment_form,
        'total_comments': comments.count(),
    }
    
    return render(request, 'blog/post_detail.html', context)


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Class-based view for creating comments"""
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment_form.html'
    
    def form_valid(self, form):
        # Get the post from URL
        post = get_object_or_404(Post, slug=self.kwargs['slug'])
        form.instance.post = post
        form.instance.author = self.request.user
        
        response = super().form_valid(form)
        messages.success(self.request, 'Your comment has been posted!')
        return response
    
    def get_success_url(self):
        return f"{self.object.post.get_absolute_url()}#comment-{self.object.id}"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = get_object_or_404(Post, slug=self.kwargs['slug'])
        return context


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """View for updating comments"""
    model = Comment
    form_class = CommentEditForm
    template_name = 'blog/comment_edit.html'
    pk_url_kwarg = 'comment_id'
    
    def test_func(self):
        """Ensure only comment author or staff can edit"""
        comment = self.get_object()
        return comment.can_edit(self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Your comment has been updated!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return f"{self.object.post.get_absolute_url()}#comment-{self.object.id}"


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """View for deleting comments"""
    model = Comment
    template_name = 'blog/comment_delete.html'
    pk_url_kwarg = 'comment_id'
    
    def test_func(self):
        """Ensure only comment author or staff can delete"""
        comment = self.get_object()
        return comment.can_delete(self.request.user)
    
    def delete(self, request, *args, **kwargs):
        comment = self.get_object()
        post_url = comment.post.get_absolute_url()
        messages.success(request, 'Comment deleted successfully!')
        
        # Actually delete the comment
        response = super().delete(request, *args, **kwargs)
        return HttpResponseRedirect(post_url)
    
    def get_success_url(self):
        return self.object.post.get_absolute_url()


@login_required
def comment_ajax_create(request, slug):
    """AJAX endpoint for creating comments (optional enhancement)"""
    if request.method == 'POST':
        post = get_object_or_404(Post, slug=slug, status='published')
        form = CommentForm(request.POST)
        
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            
            return JsonResponse({
                'success': True,
                'comment_id': comment.id,
                'author': comment.author.username,
                'content': comment.content,
                'created_at': comment.created_at.strftime('%B %d, %Y at %I:%M %p'),
                'message': 'Comment posted successfully!'
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors,
                'message': 'Please correct the errors below.'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


def user_comments(request, username):
    """View to display all comments by a specific user"""
    from django.contrib.auth.models import User
    
    user = get_object_or_404(User, username=username)
    comments = Comment.objects.filter(
        author=user,
        is_active=True,
        post__status='published'
    ).select_related('post').order_by('-created_at')
    
    # Paginate user comments
    paginator = Paginator(comments, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'profile_user': user,
        'comments': page_obj,
        'total_comments': comments.count(),
    }
    
    return render(request, 'blog/user_comments.html', context)


# Search functionality for blog posts
# This view allows users to search for blog posts by title, content, or tags.
def search_posts(request):
    query = request.GET.get('q')
    results = Post.objects.filter(
        Q(title__icontains=query) |
        Q(content__icontains=query) |
        Q(tags__name__icontains=query)
    ).distinct()
    return render(request, 'blog/search_results.html', {'results': results, 'query': query})




# Tag-based filtering for blog posts
# This view allows users to filter posts by specific tags.
def posts_by_tag(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)
    posts = Post.objects.filter(tags__name__iexact=tag.name)
    return render(request, 'blog/posts_by_tag.html', {
        'tag': tag,
        'posts': posts
    })


