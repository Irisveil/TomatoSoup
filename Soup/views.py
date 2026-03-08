from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Author, Post, Comment, HOBBY

def login_view(request):

    return render(request, 'login.html')

def signup_view(request):

    return render(request, 'signup.html')

@login_required
def home_view(request):
    author = request.user

    # My Bowl: posts from hobbies the user follows (popular-ish, newest first)
    author_hobbies = author.hobby if isinstance(author.hobby, list) and author.hobby else []
    if author_hobbies:
        feed_posts = (
            Post.objects
            .select_related("author")
            .prefetch_related("image_set")
            .filter(hobby__in=author_hobbies)
            .order_by("-views", "-published")
        )
    else:
        feed_posts = Post.objects.none()

    # What's Hot: hot posts by views (or newest via ?spotlight=newest)
    spotlight_feed = request.GET.get("spotlight", "views")
    if spotlight_feed == "newest":
        whats_new_posts = Post.objects.select_related("author").prefetch_related("image_set").order_by("-published")[:10]
    else:
        whats_new_posts = Post.objects.select_related("author").prefetch_related("image_set").order_by("-views")[:10]

    context = {
        "author": author,
        "feed_posts": feed_posts,
        "whats_new_posts": whats_new_posts,
        "spotlight_mode": spotlight_feed,
    }

    return render(request, "home.html", context)

    #return render(request, 'home.html')

@login_required
def profile_view(request):
    """
    Allows users to view their profile
    """
    author = request.user
    selected = author.hobby if isinstance(author.hobby, list) else []
    user_posts = (
        Post.objects.filter(author=author)
        .prefetch_related("image_set")
        .order_by("-published")
    )
    context = {
        "author": author,
        "all_hobbies": HOBBY,
        "selected_hobby_values": selected,
        "user_posts": user_posts,
    }
    return render(request, "profile.html", context)

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