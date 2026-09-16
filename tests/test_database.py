"""Tests for SQLite database operations, transactions, and state changes."""

from pathlib import Path
from app.database.db import init_db
from app.database.models import PageModel, PostModel, PostStatus, TopicModel, TopicStatus
from app.database.repository import Repository


def test_database_crud_flow(tmp_path: Path):
    """Test full lifecycle of topics and posts in a fresh isolated database."""
    test_db = tmp_path / "test.db"
    init_db(test_db)
    repo = Repository(test_db)

    # 1. Create Topic
    topic = TopicModel(
        id="test-topic-1",
        name="Test Topic 1",
        category="Testing",
        difficulty="beginner",
        priority=90,
        status=TopicStatus.PENDING,
    )
    repo.create_topic(topic)

    fetched = repo.get_topic("test-topic-1")
    assert fetched is not None
    assert fetched.name == "Test Topic 1"

    # 2. Next pending topic
    next_topic = repo.get_next_pending_topic()
    assert next_topic is not None
    assert next_topic.id == "test-topic-1"

    # 3. Create Post
    post = PostModel(
        topic_id="test-topic-1",
        title="Test Post Title",
        caption="Test Caption #Tag",
        status=PostStatus.DRAFT,
        content_hash="abc123hash",
    )
    saved_post = repo.create_post(post)
    assert saved_post.id > 0

    # 4. Create Pages
    page = PageModel(
        post_id=saved_post.id,
        page_number=1,
        file_path="generated/drafts/test/page_01.png",
    )
    repo.create_page(page)
    pages = repo.get_pages_for_post(saved_post.id)
    assert len(pages) == 1
    assert pages[0].page_number == 1

    # 5. Status Transitions: Draft -> Approved -> Published
    assert repo.update_post_status(saved_post.id, PostStatus.APPROVED) is True
    post_approved = repo.get_post(saved_post.id)
    assert post_approved.status == PostStatus.APPROVED
    assert post_approved.approved_at is not None

    assert repo.set_post_published(saved_post.id, instagram_media_id="ig_12345", dry_run=True) is True
    post_published = repo.get_post(saved_post.id)
    assert post_published.status == PostStatus.PUBLISHED
    assert post_published.instagram_media_id == "ig_12345"

    # 6. Dashboard Stats
    stats = repo.get_dashboard_stats()
    assert stats["total_topics"] == 1
    assert stats["published_posts"] == 1


def test_duplicate_prevention_by_hash(tmp_path: Path):
    """Verify that identical content hash can be queried to prevent duplicate generation."""
    test_db = tmp_path / "test_dup.db"
    init_db(test_db)
    repo = Repository(test_db)

    # Insert topic first to satisfy foreign key constraint
    topic = TopicModel(id="topic-1", name="Topic 1", category="General")
    repo.create_topic(topic)

    post = PostModel(
        topic_id="topic-1",
        title="Unique Post",
        caption="Caption",
        status=PostStatus.DRAFT,
        content_hash="unique_hash_xyz",
    )
    repo.create_post(post)

    existing = repo.find_post_by_hash("unique_hash_xyz")
    assert existing is not None
    assert existing.title == "Unique Post"

    not_found = repo.find_post_by_hash("non_existent_hash")
    assert not_found is None
