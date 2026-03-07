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

    # TODO: add hobby tags

    # Authentication Requirements 
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "password"]

    def __str__(self):
        return self.username

    
class Post(models.Model):
    """
    This class stores the basic information about a post
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)

    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    # TODO: add hobby tags

    published = models.DateTimeField(auto_now_add=True) # auto_now_add=True means it is only set ONCE on creation.
    views = models.PositiveIntegerField(default=0)

class Image(models.Model):
    """
    Images associated with a post
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    image = models.ImageField(upload_to='entry_images/')
    
    order = models.PositiveIntegerField(default=0)  
    
    class Meta:
        ordering = ['order']
    
    
class Comment(models.Model):
    """
    Comments associated with a post
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    
    content = models.TextField(max_length=200, blank=True)
    
    published = models.DateTimeField(auto_now_add=True)

