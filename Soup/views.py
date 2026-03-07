from django.shortcuts import render

def login_view(request):
    """
    Primary view to see all entries and their filtered variations 
    """

    return render(request, 'login.html')

def signup_view(request):
    """
    Primary view to see all entries and their filtered variations 
    """

    return render(request, 'signup.html')

# Create your views here.
@login_required
def home_view(request):
    """
    Primary view to see all entries and their filtered variations 
    """

    # return render(request, 'home.html')