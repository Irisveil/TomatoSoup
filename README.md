# TomatoSoup
We love Tomato Soup

UI: https://www.figma.com/design/buGsOhi4ZlIvRWBQLE54IX/TomatoSoup?node-id=0-1&p=f&t=NeKRcQaKPUcDdmyL-0

Workflow:
Make migrations (commit database changes): python manage.py makemigrations Soup
Migrate (apply those changes): python manage.py migrate
Run server: python manage.py runserver

FOR EACH HTML FILE:
extend base.html using (at the very top):
{% extends 'base.html' %}

Use {% block head %} {% endblock %} and {% block content %} {% endblock %} to insert the head and content
See home.html for example


idea: profile photo, friend system, dynamic topics (admin only), aria implemented

implement if have time:
filtering to allow users to peek at other hobbies
most viewed in the past 7 days

hobbies: Plants, Food, Art, Crochet, TTRPG, Books, Game, Movies, Hiking