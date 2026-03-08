from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Author, Post, Comment, HOBBY, Image, PostAgentMeta
from django.contrib.auth import logout
from django.db import transaction

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

    if isinstance(author.hobby, list):
    # My Bowl: posts from hobbies the user follows (popular-ish, newest first)
        author_hobbies = author.hobby
    elif author.hobby:
        author_hobbies = json.loads(author.hobby)
    else:
        author_hobbies = []
    
    # BOWL FEEEEEEEEED
    if author_hobbies:
        feed_posts = (
            Post.objects
            .select_related("author")
            .prefetch_related("image_set")
            .select_related("agent_meta")
            .filter(hobby__in=author_hobbies)
            .order_by("-published")
        )
    else:
        feed_posts = (
            Post.objects
            .select_related("author")
            .prefetch_related("image_set")
            .select_related("agent_meta")
            .order_by("-published")[:20]
        )

    # What's Hot: hot posts by views (or newest via ?spotlight=newest)
    spotlight_feed = request.GET.get("spotlight", "views")
    base_qs = (
        Post.objects
        .select_related("author")
        .select_related("agent_meta")
        .prefetch_related("image_set")
    )

    if spotlight_feed == "newest":
        # whats_new_posts = Post.objects.select_related("author").prefetch_related("image_set").order_by("-published")[:10]
        whats_new_posts = list(base_qs.order_by("-published")[:30])     
    else:
        #whats_new_posts = Post.objects.select_related("author").prefetch_related("image_set").order_by("-views")[:10]
        whats_new_posts = list(base_qs.order_by("-views", "-published")[:30])

    spotlight_size = 10
    max_ai = int(spotlight_size * 0.40) # Cap AI shit by 40%

    ai_posts = [p for p in whats_new_posts if hasattr(p, "agent_meta")]
    peep_posts = [p for p in whats_new_posts if not hasattr(p, "agent_meta")]

    spotlight_posts = []
    spotlight_posts.extend(ai_posts[:max_ai])
    spotlight_posts.extend(peep_posts[:spotlight_size - len(spotlight_posts)])

    if len(spotlight_posts) < spotlight_size:
        leftovers = [p for p in whats_new_posts if p not in spotlight_posts]
        spotlight_posts.extend(leftovers[:spotlight_size - len(spotlight_posts)])
    context = {
        "author": author,
        "feed_posts": feed_posts,
        "whats_new_posts": spotlight_posts,
        "spotlight_mode": spotlight_feed,
    }

    return render(request, "home.html", context)

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
        return redirect('profile')
    if author.hobby == '':
        selected = []
    else:
        selected = json.loads(author.hobby)
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
def post_view(request, post_id):
    """
    Viewing a post and allows users to comment
    """
    post = get_object_or_404(Post, pk=post_id)

    author = post.author
    comments = Comment.objects.filter(post_id=post_id).order_by("-published")
    images = Image.objects.filter(post_id=post_id).order_by("-order")
    print(len(images))

    if request.method == "POST":
        # a user has commented
        req = request.POST
        comment = Comment.objects.create(
            post=post,
            author=request.user,
            content=req['comment']
        )
        comment.save()
        return redirect('post', post_id=post.id)
    else:
        # add a view
        post.views = post.views + 1
        post.save()

    context = {
        "post": post,
        "author": author,
        "comments": comments,
        "images": images
    }

    return render(request, "post.html", context)

@login_required
def create_post_view(request):
    """
    Allows users to create a post
    """

    if request.method == "POST": # if user is posting the new post
        req = request.POST
        images = request.FILES.getlist("images")

        # TODO: sanitize the content?

        with transaction.atomic(): # make sure everything in together
            post = Post.objects.create(
                author=request.user,
                title=req['title'],
                description=req['content'],
                hobby=req['hobby'],
                views=0
            )
            post.save()

            i = 0
            for img in images:
                image = Image.objects.create(
                    post=post,
                    image=img,
                    order=i
                )
                image.save()
                i += 1
        # redirect to home page
        return redirect('home')

    else:
        context = {"all_hobbies": HOBBY}
        return render(request, "create_post.html", context)