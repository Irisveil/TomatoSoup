from django.db import models
from django.utils import timezone
from django.contrib.auth.base_user import AbstractBaseUser
# from django.contrib.postgres.fields import JSONField
import uuid

# Create your models here.
class Author(AbstractBaseUser):
    '''
    This class stores the basic information about a user
    '''
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150, unique=True)
    email = models.CharField(blank=True)
    password = models.CharField(max_length=128, default="thisisapassword")

    date_joined = models.DateTimeField(default=timezone.now)
    is_admin = models.BooleanField(default=False)

    # TODO: this will be a list of their selected interests
    interests = models

    # Authentication Requirements 
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["username", "email", "password"]

    def __str__(self):
        return self.username

    
class Post(models.Model):
    """
    This class stores the basic information about a post
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)

    # TODO: link to author

    # TODO: images

    # TODO: this is the hobby tags
    interests


    published = models.DateTimeField(auto_now_add=True) # auto_now_add=True means it is only set ONCE on creation.
    views = models.PositiveIntegerField(default=0)


    def __str__(self):
        return f"Entry by {self.author} ({self.visibility})"


class EntryImage(models.Model):
    """
    Multiple images can be associated with a single Entry.
    Access via: entry.images.all()
    """
    id = models.URLField(primary_key=True, unique=True)
    entry = models.ForeignKey(
        Entry,
        on_delete=models.CASCADE,
        related_name='images',
        blank = True,
        null = True
        
    )
    name = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to='entry_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    order = models.PositiveIntegerField(default=0)  
    
    class Meta:
        ordering = ['order', 'uploaded_at']
    
    def __str__(self):
        if self.entry:
            return f"Image for entry {self.entry.id}"
        return f"Standalone Image {self.id}"  # or just "Standalone Image"
    
class Comment(models.Model):
    """
    Comment object (federated). ID is the FQID of the comment.
    Example id: "http://nodeaaaa/api/authors/111/commented/130"
    """
    id = models.URLField(primary_key=True, unique=True) # FQID
    type = models.CharField(max_length=20, default="comment", editable=False)
    author = models.ForeignKey(
        Author, 
        to_field='id',
        db_column='author_id',
        on_delete=models.CASCADE, 
        related_name="comment"
    )
    entry = models.ForeignKey(
        Entry,
        to_field='id',
        db_column='entry_id',
        on_delete=models.CASCADE, 
        related_name="comment"
    )
    content = models.TextField(max_length=200, blank=True)
    contentType = models.CharField(max_length=100, default="text/markdown")
    reply_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    published = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(
        'Author',
        related_name='liked_comments',
        blank=True
    )
    def like_count(self):
        return Like.objects.filter(object=self.id).count()
