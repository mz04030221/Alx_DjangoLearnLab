from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
from django.urls import reverse 
from django.utils.text import slugify
from taggit.managers import TaggableManager



# Blog Post Model
# This model represents a blog post in the application.
# It includes fields for the post title, content, published date, and author.
# The title is a CharField with a maximum length of 200 characters.
class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    published_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    #slug = models.SlugField(unique=True, blank=True)
    slug = models.SlugField(null=True, blank=True) 
    tags = TaggableManager()  # Allows tagging of posts


    def save(self, *args, **kwargs): 
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

       
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk}) # URL for the post detail view
    
    class Meta:
        ordering = ['-published_date']  # Show newest posts first



# title: CharField with max 200 characters for the blog post title
# content: TextField for the main blog post content (unlimited length)
# published_date: DateTimeField that automatically sets the date/time when a post is created
# author: ForeignKey linking to Django's built-in User model
# on_delete=models.CASCADE: If a user is deleted, their posts are also deleted
# related_name='blog_posts': Allows you to access a user's posts with user.blog_posts.all()
# __str__: Returns the title when the model is printed (useful in Django admin)
# Meta.ordering: Orders posts by newest first (the - means descending order)



# User Profile Model
# This model extends the User model to include additional fields for user profiles.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    # profile_picture: ImageField to store user's profile picture
    # default='default.jpg': Use a default image if none is uploaded
    profile_picture = models.ImageField(default='profile_pics/default.jpg', upload_to='profile_pics')
    website = models.URLField(max_length=200, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Resize image if it's too large
        img = Image.open(self.profile_picture.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.profile_picture.path)

# Create a profile automatically when a user is created
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()



# This model represents comments on blog posts.
# It includes fields for the post, author, content, and timestamps.
class Comment(models.Model):
    post = models.ForeignKey(
        Post, 
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField(
        max_length=1000,
        help_text="Share your thoughts (max 1000 characters)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Optional: Add moderation fields
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['created_at']  # Oldest comments first
        indexes = [
            models.Index(fields=['post', '-created_at']),
            models.Index(fields=['author', '-created_at']),
        ]

    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.post.slug}) + f'#comment-{self.id}'

    def can_edit(self, user):
        """Check if a user can edit this comment"""
        return self.author == user or user.is_staff

    def can_delete(self, user):
        """Check if a user can delete this comment"""
        return self.author == user or user.is_staff