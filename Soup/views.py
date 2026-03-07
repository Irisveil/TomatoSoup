from django.shortcuts import render

# Create your views here.
def home_view(request):
    """
    Primary view to see all entries and their filtered variations 
    """

    # return render(request, 'home.html')