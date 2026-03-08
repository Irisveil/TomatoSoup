from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Author, Post, Comment, HOBBY
from django.contrib.auth import logout

from django.contrib.auth.forms import UserCreationForm
from django import forms

# custom forms
class CustomForm(UserCreationForm):
    username = forms.CharField(max_length=100, required=True)
    email = forms.CharField(max_length=100, required=True)
    password1 = forms.CharField(max_length=20, required=True)
    password2 = forms.CharField(max_length=20, required=True)

    class Meta(UserCreationForm.Meta):
        model = Author
        fields = ('username', 'password1', 'password2', 'email')

def signup_view(request):
    logout(request)

    if request.method == "POST": # if user signing up
        form = CustomForm(request.POST)
        
        # validate inputs
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            return redirect('profile')
    else:
        form = CustomForm()

    return render(request, "signup.html", {"form": form})

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