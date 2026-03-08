from django.urls import path
from . import views
from django.contrib.auth.views import LoginView

urlpatterns = [
    path('login/', LoginView.as_view(template_name="login.html"), name='login'),
    path('signup/', views.signup_view, name='signup'),

    path('home/', views.home_view, name='home'),
    path('profile/', views.profile_view, name='profile'),

    path('post/<str:post_id>/', views.post_view, name='post'),
    path('newpost/', views.create_post_view, name='new_post'),
]