from django.urls import path
from . import views
from django.contrib.auth.views import LoginView

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('login/', LoginView.as_view(template_name="login.html"), name='login'),
    path('signup/', views.signup_view, name='signup'),

    path('', views.home_view, name='home'),
    path('profile/', views.profile_view, name='profile'),

    path('post/<str:post_id>/', views.post_view, name='post'),
    path('newpost/', views.create_post_view, name='new_post'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)