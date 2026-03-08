# TomatoSoup

**TomatoSoup** is a hobby-focused community platform where people share posts, discover content, and connect around the things they love

## What is TomatoSoup?

TomatoSoup lets you:

- **Choose your hobbies** — Pick from a variety of topics
- **Fill your Bowl** — Your feed (“My Bowl”) shows posts from the hobbies you follow, newest first.
- **See what’s hot** — A spotlight section highlights popular or newest posts across the community.
- **Post and comment** — Create posts with titles, descriptions, and images, and join the conversation with comments.
- **Build your profile** — Sign up, set your interests, and have a place to share and discover.

It’s built with **Django**, with a custom `Author` model, hobby-based feeds, and a template system that keeps the UI consistent and easy to extend.

## Getting started

### Prerequisites

- Python 3
- Django project set up (see project root for `manage.py`)

### Run locally

```bash
# Create and apply database migrations
python manage.py makemigrations Soup
python manage.py migrate

# Start the development server
python manage.py runserver
```

### UI design

Figma design: [TomatoSoup (Figma)](https://www.figma.com/design/buGsOhi4ZlIvRWBQLE54IX/TomatoSoup?node-id=0-1&p=f&t=NeKRcQaKPUcDdmyL-0)

## For developers

### Templates

- **Base template:** Extend `base.html` at the top of every HTML file:
  ```django
  {% extends 'base.html' %}
  ```
- Use `{% block head %}{% endblock %}` and `{% block content %}{% endblock %}` for page-specific head and content.
- See `home.html` for a full example.

### Roadmap / ideas

- *If time allows:* filtering to peek at other hobbies, “most viewed in the past 7 days.”
- Create a new tab where user can access more feeds specific to the hobby (Look into different "Bowls")

---

We love Tomato Soup.
@ 2019 Cult. of the Soup*


*Cult. is abbreviation for Culture