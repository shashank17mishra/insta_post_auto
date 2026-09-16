"""Deduplication service ensuring topics and notes are not duplicated."""

import re
from typing import Optional
from app.content.schemas import NotePostContent
from app.database.models import PostModel
from app.database.repository import Repository
from app.utils.hashing import compute_content_hash


def normalize_topic_name(name: str) -> str:
    """Normalize a topic name for comparison (removes punctuation, lowercases)."""
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", "", name.lower())
    return " ".join(cleaned.split())


def compute_post_hash(content: NotePostContent) -> str:
    """Compute deterministic SHA-256 hash of post content payload."""
    payload = {
        "topic": normalize_topic_name(content.topic),
        "title": content.title.strip().lower(),
        "pages": [
            {
                "heading": p.heading.strip().lower(),
                "sections": [
                    {
                        "heading": s.heading.strip().lower(),
                        "body": s.body.strip(),
                        "formula": s.formula,
                        "code": s.code,
                    }
                    for s in p.sections
                ],
            }
            for p in content.pages
        ],
    }
    return compute_content_hash(payload)


def is_topic_already_published(repo: Repository, topic_id: str) -> bool:
    """Check if the given topic has already been published."""
    post = repo.get_post_by_topic(topic_id)
    return post is not None and post.status.value == "published"


def find_similar_existing_post(repo: Repository, content: NotePostContent) -> Optional[PostModel]:
    """Check if an identical post content hash is already stored."""
    c_hash = compute_post_hash(content)
    return repo.find_post_by_hash(c_hash)
