from django.db import models
from django.utils import timezone
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db.models import JSONField, Q
import uuid

HOBBY = [
    ("PLANTS", "Plants"),
    ("ART", "Art"),
    ("FOOD", "Food"),
    ("CROCHET", "Crochet"),
    ("TTRPG", "TTRPG"),
    ("BOOKS", "Books"),
    ("GAMES", "Games"),
    ("MOVIES", "Movies"),
    ("HIKING", "Hiking"),
]

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        # TODO: check for email validity
        if not email:
            raise ValueError("Email required")
        if not username:
            raise ValueError("Username required")
        if not password:
            raise ValueError("Password required")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.id = uuid.uuid4()
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        return self.create_user(username, email, password, **extra_fields)

class Author(AbstractBaseUser, PermissionsMixin):
    '''
    This class stores the basic information about a user
    '''
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150, unique=True)
    email = models.CharField(blank=True)
    password = models.CharField(max_length=128, default="thisisapassword")
    pronouns = models.CharField(max_length=128, default="")
    hobby = JSONField(default='') # This will be a list of strings of hobbies that the user has selected

    date_joined = models.DateTimeField(default=timezone.now)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    objects = UserManager()

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
    hobby = models.CharField(max_length=300, choices=HOBBY, default='PLANTS')

    published = models.DateTimeField(default=timezone.now)
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
    
    published = models.DateTimeField(default=timezone.now)

class HobbyTag(models.Model):
    """
    This class stores the hobbies 
    """
    slug = models.SlugField(max_length = 50, unique = True)
    label = models.CharField(max_length = 100, unique = True)

    def __str__(self):
        return self.label
    
class TopicCandidate(models.Model):
    
    class Status(models.TextChoices):
        NEW = 'NEW', 'New'
        KEPT = 'KEPT', 'Kept'
        REJECTED = 'REJECTED', 'Rejected'
        POSTED = 'POSTED', 'Posted'

    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    source_name = models.CharField(max_length = 120)
    source_url = models.URLField(max_length = 500)
    title = models.CharField(max_length = 300)
    summary = models.TextField(blank = True)
    published_at = models.DateTimeField()
    region = models.CharField(max_length=120, default = "province-wide")
    raw_hash = models.CharField(max_length = 64, unique = True)
    matched_tags = models.ManyToManyField(HobbyTag, blank = True)
    score = models.FloatField(default = 0.0)
    status = models.CharField(max_length = 20, choices = Status.choices, default = Status.NEW)  
    created_at = models.DateTimeField(auto_now_add = True)

    class Meta:
        ordering = ['-published_at']
        indexes = [
            models.Index(fields = ['status']),
            models.Index(fields = ['published_at']),
            models.Index(fields = ['score']),
        ]

    def __str__(self):
        return self.title
    
class AgentRun(models.Model):
    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    started_at = models.DateTimeField(default = timezone.now)
    finished_at = models.DateTimeField(null = True, blank = True)
    items_fetched = models.PositiveIntegerField(default = 0)
    items_kepts = models.PositiveIntegerField(default = 0)
    posts_created = models.PositiveIntegerField(default = 0)
    errors = models.TextField(blank = True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"AgentRun {self.started_at:%Y-%m-%d %H:%M}"
    
class PostAgentMeta(models.Model):

    class OriginType(models.TextChoices):
        EXTERNAL_TOPIC = 'external_topic', 'External Topic'
        REVIVED_POST = 'revived_post', 'Revived Post'

    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    post = models.OneToOneField(Post, on_delete = models.CASCADE, related_name='agent_meta')
    origin_type = models.CharField(max_length = 30, choices = OriginType.choices)

    topic_candidate = models.ForeignKey(
        TopicCandidate,
        on_delete = models.SET_NULL,
        null = True,
        blank = True,
        related_name = 'published_posts',
    )

    revived_from_post = models.ForeignKey(
        'Post',
        on_delete = models.SET_NULL,
        null = True,
        blank = True,
        related_name = 'revived_by_agent_meta',
    )

    model_name = models.CharField(max_length = 120, blank = True)
    safety_passed = models.BooleanField(default = False)
    created_at = models.DateTimeField(auto_now_add = True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check = Q(topic_candidate__isnull = False) | Q(revived_from_post__isnull = False),
                name = 'post_agent_meta_origin_link',
            )
        ]

    def __str__(self):
        return f"AgentMeta for {self.post_id}"
