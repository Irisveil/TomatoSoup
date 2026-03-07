from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def login_view(request):

    return render(request, 'login.html')

def signup_view(request):

    return render(request, 'signup.html')

# Create your views here.
@login_required
def home_view(request):
    """
    Primary view to see all entries
    """

    return render(request, 'home.html')

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

    # return render(request, 'post.html')

@login_required
def create_post_view(request):
    """
    Allows users to create a post
    """

    # return render(request, 'create_post.html')