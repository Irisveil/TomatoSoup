from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='login'),

    path('home/', views.home_view, name='home'),
    path('profile/', views.profile_view, name='profile'),

    path('post/<str:post_id>/', views.post_view, name='post'),
    path('newpost/', views.create_post_view, name='new_post'),
]