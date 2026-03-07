from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Author, Post, Comment

def login_view(request):

    return render(request, 'login.html')

def signup_view(request):

    return render(request, 'signup.html')

# Create your views here.

@login_required
def home_view(request):
    # IS this bittttch logged in?
    author = request.user

    # Author's feed of posts with others that share their hobby
    feed_posts = (
        Post.objects
        .select_related("author")
        .prefetch_related("image_set")
        # TODO: 
        .filter(author__hobbies__in=author.hobbies.all())
        .distinct()
        .order_by("-published")
    )
    
    # Spotlight on either the newest or the most views
    spotlight_feed = request.GET.get("spotlight", "newest")
    if spotlight_feed == "views":
        spotlight_feed = Post.objects.order_by("-views")[:5]
    else:
        spotlight_feed = Post.objects.order_by("-published")[:5]

    # Live chat
    live_chat = (
        Comment.objects
        .select_related("author", "post")
        .order_by("-published")[:15]
    )

    context = {
        "author": author,
        "feed_posts": feed_posts,
        "spotlight_feed": spotlight_feed,
        "live_chat": live_chat,
    }

    return render(request, "home.html", context)

    # return render(request, 'post.html')

@login_required
def profile_view(request):
    """
    Allows users to view their profile
    """

    return render(request, 'profile.html')

@login_required
def post_view(request):
    """
    Viewing a post and allows users to comment
    """

@login_required
def create_post_view(request):
    """
    Allows users to create a post
    """

    # return render(request, 'create_post.html')