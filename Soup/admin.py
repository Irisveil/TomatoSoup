from django.contrib import admin

# Register your models here.
from .models import Author, Post, Image, Comment

"""
This module allows us to manipulate our database using the Django Admin panel.
"""

models_class = [Author, Post, Image, Comment]
for model in models_class:
    admin.site.register(model)