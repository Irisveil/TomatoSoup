# PIPELINE FUNCTIONS FOUR OUR DISCUSSION AGENT

import hashlib
from datetime import timedelta
from difflib import SequenceMatcher

import feedparser
import requests
from dateutil import parser as date_parser
from django.db import transaction
from django.db.models import Count, F, FloatField, Q, ExpressionWrapper, Max
from django.utils import timezone

from Soup.models import Author, Comment, Post, AgentRun, HobbyTag, PostAgentMeta, TopicCandidate


HOBBY_KEYWORDS = {
    "books": ["book", "novel", "author", "reading", "literature", "fiction", "non-fiction", "poetry", "biography"],
    "movies": ["movie", "film", "cinema", "trailer", "director", "actor", "theater"],
    "games": ["game", "gaming", "board game", "catan", "cards", "gloomhaven"],
    "art": ["art", "gallery", "painting", "illustration", "museum", "sculpture", "painting", "drawing"],
    "hiking": ["hike", "hiking", "trail", "outdoor", "park", "mountain", "nature"],
    "ttrpg": ["ttrpg", "dnd", "d&d", "tabletop", "campaign", "rpg", "5e"],
    "plants": ["plant", "gardening", "botany", "succulent", "houseplant"],
    "crochet": ["crochet", "yarn", "knit", "needlework", "fiber art"],
}

RSS_SOURCES = [
    ("Gutenberg Today", "https://www.gutenberg.org/cache/epub/feeds/today.rss"),
    ("Guardian Books", "https://www.theguardian.com/books/rss"),
    ("Guardian Film", "https://www.theguardian.com/film/rss"),
    ("Guardian Games", "https://www.theguardian.com/games/rss"),
    ("Guardian Art and Design", "https://www.theguardian.com/artanddesign/rss"),
    ("Guardian Travel", "https://www.theguardian.com/uk/travel/rss"),
    ("Guardian Life and Style", "https://www.theguardian.com/lifeandstyle/rss"),
]


# Optional local event endpoint places
EVENT_API_URLS = []

def normalize_item(source_name, source_url, title, summary, published_at, region = "province-wide"):
    """
    Normalize the input data and create a unique hash for deduplication
    """
    raw = f"{source_name} | {source_url} | {title} | {published_at.isoformat()}"
    raw_hash = hashlib.sha256(raw.encode('utf-8')).hexdigest()
    return {
        "source_name": source_name,
        "source_url": source_url,
        "title": title[:300],  # Truncate to fit model constraints
        "summary": summary or "",
        "published_at": published_at,
        "region": region,
        "raw_hash": raw_hash,
    }

def ingest_topics(days_back=7):
    cutoff = timezone.now() - timedelta(days=days_back)
    kept = []
    fetched_count = 0

    # RSS ingestion
    for source_name, feed_url in RSS_SOURCES:
        feed = feedparser.parse(feed_url)
        entries = getattr(feed, "entries", [])
        fetched_count += len(entries)

        for entry in entries:
            title = getattr(entry, "title", "") or ""
            summary = getattr(entry, "summary", "") or ""
            link = getattr(entry, "link", feed_url)

            published_raw = getattr(entry, "published", None) or getattr(entry, "updated", None)
            if published_raw:
                dt = date_parser.parse(published_raw)
                if timezone.is_naive(dt):
                    dt = timezone.make_aware(dt, timezone.get_current_timezone())
            else:
                dt = timezone.now()

            if dt < cutoff:
                continue

            normalized = normalize_item(source_name, link, title, summary, dt)
            obj, created = TopicCandidate.objects.get_or_create(
                raw_hash=normalized["raw_hash"],
                defaults=normalized,
            )
            if created:
                kept.append(obj)

    # Optional events API ingestion
    for url in EVENT_API_URLS:
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            continue

        for item in data:
            fetched_count += 1
            title = item.get("title", "")
            summary = item.get("description", "")
            link = item.get("url", url)

            published_raw = item.get("published_at")
            if published_raw:
                dt = date_parser.parse(published_raw)
                if timezone.is_naive(dt):
                    dt = timezone.make_aware(dt, timezone.get_current_timezone())
            else:
                dt = timezone.now()

            if dt < cutoff:
                continue

            normalized = normalize_item("EventsAPI", link, title, summary, dt)
            obj, created = TopicCandidate.objects.get_or_create(
                raw_hash=normalized["raw_hash"],
                defaults=normalized,
            )
            if created:
                kept.append(obj)

    return fetched_count, kept

    
def classify_topics_to_hobbies(candidates):
    tags_by_slug = {t.slug: t for t in HobbyTag.objects.all()}
    kept = []

    for candidate in candidates:
        text = f"{candidate.title} {candidate.summary}".lower()
        matched = []

        for slug, keywords in HOBBY_KEYWORDS.items():
            if any(k in text for k in keywords) and slug in tags_by_slug:
                matched.append(tags_by_slug[slug])

        if matched:
            candidate.matched_tags.set(matched)
            candidate.status = TopicCandidate.Status.KEPT
            candidate.save(update_fields = ['status'])
            kept.append(candidate)
        else:
            candidate.status = TopicCandidate.Status.REJECTED
            candidate.save(update_fields = ['status'])

    return kept
    

def rank_revival_candidates(limit = 20):
    now = timezone.now()
    max_age_days = 120

    posts = (
        Post.objects.annotate(comment_count = Count('comment'))
        .filter(published__gte = now - timedelta(days = max_age_days))
    )

    max_views = posts.aggregate(v = Max('views'))['v'] or 1
    max_comments = posts.aggregate(c = Max('comment_count'))['c'] or 1

    ranked = []
    for post in posts:
        age_days = max((now - post.published).days, 0)
        recency_norm = max(0.0, 1.0 - (age_days / max_age_days))
        comment_norm = post.comment_count / max_comments
        view_norm = post.views / max_views

        score = (comment_norm * 0.65) + (view_norm * 0.20) + (recency_norm * 0.15)
        ranked.append((post, score))

    ranked.sort(key = lambda x: x[1], reverse = True)
    return ranked[:limit]

def generate_discussion_post(title_seed, summary_seed, tag_slugs):
    tags_text = ", ".join(tag_slugs[:3]) if tag_slugs else 'community'
    title = f"Community Topic: {title_seed[:220]}"
    body = (
        f"{summary_seed[:800]}\n\n"
        f"What do you think about this in the context of {tags_text}?"
    )

    return title, body

def _similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def safety_filter(title, body, tag_slugs):
    if not tag_slugs:
        return False, "no_tag"

    blocked_words = ['nsfw', 'jew', 'retard', 'munging', 'nazi', 'nigger', 'cunt', 'chink', 'faggot']
    text = f"{title} {body}".lower()

    if any(w in text for w in blocked_words):
        return False, "blocked_content"

    recent_posts = Post.objects.order_by("-published")[:100]
    for p in recent_posts:
        if _similarity(title, p.title or '') > 0.92:
            return False, 'duplicate_title'
        
        if _similarity(body, p.description or '') > 0.94:
            return False, 'duplicate_body'

    return True, "ok"

def get_or_create_system_author():
    username = "tomatosoup_agent"
    author = Author.objects.filter(username = username).first()

    if author:
        return author

    author = Author(
        username = username,
        email = "agent@tomatosoup.local",
        hobby = [],
        is_staff = False,
        is_superuser = False,
        is_active = True,
    )

    author.set_password("disabled-account-password")
    author.save()
    return author

@transaction.atomic
def publish_post(origin_type, title, body, tags, *, topic_candidate = None, revived_from_post = None, model_name = "rules-v1"):
    system_author = get_or_create_system_author()

    # Pick first tag for Post.hobby (current model is single hobby)
    hobby_choice = "PLANTS"

    if tags:
        hobby_choice = tags[0].upper() if tags[0].upper() in dict(Post._meta.get_field("hobby").choices) else "PLANTS"

    post = Post.objects.create(
        title = title,
        description = body,
        author = system_author,
        hobby = hobby_choice,
        published = timezone.now(),
    )

    PostAgentMeta.objects.create(
        post = post,
        origin_type = origin_type,
        topic_candidate = topic_candidate,
        revived_from_post = revived_from_post,
        model_name = model_name,
        safety_passed = True,
    )

    return post

def ai_posted_recently(hobby_value, hours = 24):
    cutoff = timezone.now() - timedelta(hours = hours)

    return PostAgentMeta.objects.filter(
        post__hobby = hobby_value,
        post__published__gte = cutoff,
    ).exists()

def run_agent_once(dry_run = False, external_cap = 3, revival_cap = 2):
    run = AgentRun.objects.create(started_at = timezone.now())
    posts_created = 0

    try:
        fetched_count, new_candidates = ingest_topics(days_back = 7)
        kept_candidates = classify_topics_to_hobbies(new_candidates)

        run.items_fetched = fetched_count
        run.items_kepts = len(kept_candidates) # model uses items_kepts
        run.save(update_fields = ['items_fetched', 'items_kepts'])

        # External topics
        for candidate in kept_candidates[:external_cap]:
            tag_slugs = list(candidate.matched_tags.values_list("slug", flat=True))
            title, body = generate_discussion_post(candidate.title, candidate.summary, tag_slugs)
            ok, _reason = safety_filter(title, body, tag_slugs)
            if not ok:
                candidate.status = TopicCandidate.Status.REJECTED
                candidate.save(update_fields=["status"])
                continue

            hobby_value = "PLANTS"
            if tag_slugs:
                candidate_hobby = tag_slugs[0].upper()
                valid_choices = dict(Post._meta.get_field("hobby").choices)
                if candidate_hobby in valid_choices:
                    hobby_value = candidate_hobby
            
            if ai_posted_recently(hobby_value, hours = 24):
                continue

            if not dry_run:
                publish_post(
                    origin_type=PostAgentMeta.OriginType.EXTERNAL_TOPIC,
                    title=title,
                    body=body,
                    tags=tag_slugs,
                    topic_candidate=candidate,
                    model_name="rules-v1",
                )
                candidate.status = TopicCandidate.Status.POSTED
                candidate.save(update_fields=["status"])
                posts_created += 1    

        # Revival posts
        revival_ranked = rank_revival_candidates(limit=20)
        for post, score in revival_ranked[:revival_cap]:
            seed = post.title or "Interesting community thread"
            summary = post.description or "This topic previously generated discussion."
            tags = [post.hobby.lower()]
            title, body = generate_discussion_post(f"Revisit: {seed}", summary, tags)
            ok, _reason = safety_filter(title, body, tags)
            if not ok:
                continue

            if ai_posted_recently(post.hobby, hours = 24):
                continue

            if not dry_run:
                publish_post(
                    origin_type=PostAgentMeta.OriginType.REVIVED_POST,
                    title=title,
                    body=body,
                    tags=tags,
                    revived_from_post=post,
                    model_name="rules-v1",
                )
                posts_created += 1

        run.posts_created = posts_created
        run.finished_at = timezone.now()
        run.save(update_fields=["posts_created", "finished_at"])

    except Exception as exc:
        run.errors = str(exc)
        run.finished_at = timezone.now()
        run.save(update_fields=["errors", "finished_at"])
        raise

    return run

