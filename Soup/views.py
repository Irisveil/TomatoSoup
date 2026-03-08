from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Author, Post, Comment, HOBBY
from django.contrib.auth import logout

from django.contrib.auth.forms import UserCreationForm
from django import forms
import json

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
    if request.method == "POST": # if user is editing something
        req = request.POST
        if 'email' in req: # updating user information
            author.username = req['username']
            author.email = req['email']
            author.pronouns = req['pronouns']
            author.save()
        else: # updating hobby preferences
            if author.hobby == '':
                hobbi = []
            else:
                hobbi = json.loads(author.hobby)
            if req['hobby'] not in hobbi:
                hobbi.append(req['hobby'])
                author.hobby = json.dumps(hobbi)
                author.save()
            else:
                hobbi.remove(req['hobby'])
                author.hobby = json.dumps(hobbi)
                author.save()

    selected = json.loads(author.hobby)
    user_posts = (
        Post.objects.filter(author=author)
        .prefetch_related("image_set")
        .order_by("-published")
    )
    print(selected)
    print(HOBBY)
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