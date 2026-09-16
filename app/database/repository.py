"""Database repository implementing CRUD and business queries."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from app.database.db import get_connection
from app.database.models import (
    PageModel,
    PostModel,
    PostStatus,
    PublishAttemptModel,
    TopicModel,
    TopicStatus,
)
from app.logging_config import logger


class Repository:
    """Central repository for database transactions."""

    def __init__(self, db_path: Path = None):
        self.db_path = db_path

    # =========================================================================
    # Topics
    # =========================================================================

    def create_topic(self, topic: TopicModel) -> TopicModel:
        """Insert or ignore a topic by ID."""
        with get_connection(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO topics (id, name, category, difficulty, status, priority, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    topic.id,
                    topic.name,
                    topic.category,
                    topic.difficulty,
                    topic.status.value if isinstance(topic.status, TopicStatus) else topic.status,
                    topic.priority,
                    topic.created_at,
                    topic.updated_at,
                ),
            )
        return topic

    def get_topic(self, topic_id: str) -> Optional[TopicModel]:
        """Fetch topic by ID."""
        with get_connection(self.db_path) as conn:
            row = conn.execute("SELECT * FROM topics WHERE id = ?", (topic_id,)).fetchone()
            if not row:
                return None
            return TopicModel(**dict(row))

    def get_topic_by_name(self, name: str) -> Optional[TopicModel]:
        """Fetch topic by exact name (case-insensitive)."""
        with get_connection(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM topics WHERE LOWER(name) = LOWER(?) LIMIT 1", (name.strip(),)
            ).fetchone()
            if not row:
                return None
            return TopicModel(**dict(row))

    def list_topics(
        self,
        category: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[TopicModel]:
        """List topics with optional filters."""
        query = "SELECT * FROM topics WHERE 1=1"
        params: list[Any] = []
        if category:
            query += " AND category = ?"
            params.append(category)
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY priority DESC, id ASC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        with get_connection(self.db_path) as conn:
            rows = conn.execute(query, tuple(params)).fetchall()
            return [TopicModel(**dict(r)) for r in rows]

    def get_next_pending_topic(self, category: Optional[str] = None) -> Optional[TopicModel]:
        """Select the highest priority pending topic."""
        query = "SELECT * FROM topics WHERE status = 'pending'"
        params: list[Any] = []
        if category:
            query += " AND category = ?"
            params.append(category)
        query += " ORDER BY priority DESC, id ASC LIMIT 1"

        with get_connection(self.db_path) as conn:
            row = conn.execute(query, tuple(params)).fetchone()
            if not row:
                return None
            return TopicModel(**dict(row))

    def update_topic_status(self, topic_id: str, status: TopicStatus) -> bool:
        """Update status of a topic."""
        now = datetime.now(timezone.utc).isoformat()
        with get_connection(self.db_path) as conn:
            cur = conn.execute(
                "UPDATE topics SET status = ?, updated_at = ? WHERE id = ?",
                (status.value if isinstance(status, TopicStatus) else status, now, topic_id),
            )
            return cur.rowcount > 0

    def seed_topics_from_file(self, file_path: Path) -> int:
        """Load and upsert topics from a JSON file."""
        if not file_path.exists():
            return 0
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        count = 0
        now = datetime.now(timezone.utc).isoformat()
        with get_connection(self.db_path) as conn:
            for item in data:
                topic_id = item.get("id") or item.get("topic", "").lower().replace(" ", "-")
                name = item.get("topic") or item.get("name")
                category = item.get("category", "General")
                difficulty = item.get("difficulty", "beginner")
                priority = item.get("priority", 50)
                status = item.get("status", "pending")

                conn.execute(
                    """
                    INSERT INTO topics (id, name, category, difficulty, status, priority, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        name = excluded.name,
                        category = excluded.category,
                        difficulty = excluded.difficulty,
                        priority = excluded.priority,
                        updated_at = excluded.updated_at
                    """,
                    (topic_id, name, category, difficulty, status, priority, now, now),
                )
                count += 1
        logger.info(f"Seeded/updated {count} topics in database.")
        return count

    # =========================================================================
    # Posts
    # =========================================================================

    def create_post(self, post: PostModel) -> PostModel:
        """Create a new post record and populate autoincrement ID."""
        with get_connection(self.db_path) as conn:
            cur = conn.execute(
                """
                INSERT INTO posts (topic_id, title, caption, hashtags, status, content_hash, dry_run, created_at, approved_at, published_at, instagram_media_id, error)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    post.topic_id,
                    post.title,
                    post.caption,
                    post.hashtags,
                    post.status.value if isinstance(post.status, PostStatus) else post.status,
                    post.content_hash,
                    1 if post.dry_run else 0,
                    post.created_at,
                    post.approved_at,
                    post.published_at,
                    post.instagram_media_id,
                    post.error,
                ),
            )
            post.id = cur.lastrowid
        return post

    def get_post(self, post_id: int) -> Optional[PostModel]:
        """Fetch post by ID."""
        with get_connection(self.db_path) as conn:
            row = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
            if not row:
                return None
            data = dict(row)
            data["dry_run"] = bool(data.get("dry_run"))
            return PostModel(**data)

    def find_post_by_hash(self, content_hash: str) -> Optional[PostModel]:
        """Find an existing post with matching content hash."""
        if not content_hash:
            return None
        with get_connection(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM posts WHERE content_hash = ? ORDER BY id DESC LIMIT 1",
                (content_hash,),
            ).fetchone()
            if not row:
                return None
            data = dict(row)
            data["dry_run"] = bool(data.get("dry_run"))
            return PostModel(**data)

    def get_post_by_topic(self, topic_id: str) -> Optional[PostModel]:
        """Find the latest post for a given topic."""
        with get_connection(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM posts WHERE topic_id = ? ORDER BY id DESC LIMIT 1",
                (topic_id,),
            ).fetchone()
            if not row:
                return None
            data = dict(row)
            data["dry_run"] = bool(data.get("dry_run"))
            return PostModel(**data)

    def list_posts(self, status: Optional[str] = None, limit: int = 50) -> list[PostModel]:
        """List posts filtered optionally by status."""
        query = "SELECT * FROM posts WHERE 1=1"
        params: list[Any] = []
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)

        with get_connection(self.db_path) as conn:
            rows = conn.execute(query, tuple(params)).fetchall()
            result = []
            for r in rows:
                d = dict(r)
                d["dry_run"] = bool(d.get("dry_run"))
                result.append(PostModel(**d))
            return result

    def update_post_status(self, post_id: int, status: PostStatus, error: Optional[str] = None) -> bool:
        """Update status and optional error message on a post."""
        now = datetime.now(timezone.utc).isoformat()
        with get_connection(self.db_path) as conn:
            if status == PostStatus.APPROVED:
                cur = conn.execute(
                    "UPDATE posts SET status = ?, approved_at = ?, error = ? WHERE id = ?",
                    (status.value, now, error, post_id),
                )
            else:
                cur = conn.execute(
                    "UPDATE posts SET status = ?, error = ? WHERE id = ?",
                    (status.value, error, post_id),
                )
            return cur.rowcount > 0

    def set_post_published(self, post_id: int, instagram_media_id: str, dry_run: bool = False) -> bool:
        """Mark post as successfully published."""
        now = datetime.now(timezone.utc).isoformat()
        with get_connection(self.db_path) as conn:
            cur = conn.execute(
                """
                UPDATE posts
                SET status = 'published',
                    published_at = ?,
                    instagram_media_id = ?,
                    dry_run = ?,
                    error = NULL
                WHERE id = ?
                """,
                (now, instagram_media_id, 1 if dry_run else 0, post_id),
            )
            return cur.rowcount > 0

    # =========================================================================
    # Pages
    # =========================================================================

    def create_page(self, page: PageModel) -> PageModel:
        """Store page image reference."""
        with get_connection(self.db_path) as conn:
            cur = conn.execute(
                """
                INSERT INTO pages (post_id, page_number, file_path, width, height, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    page.post_id,
                    page.page_number,
                    page.file_path,
                    page.width,
                    page.height,
                    page.created_at,
                ),
            )
            page.id = cur.lastrowid
        return page

    def get_pages_for_post(self, post_id: int) -> list[PageModel]:
        """Fetch all pages for a post in order."""
        with get_connection(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM pages WHERE post_id = ? ORDER BY page_number ASC",
                (post_id,),
            ).fetchall()
            return [PageModel(**dict(r)) for r in rows]

    # =========================================================================
    # Publish Attempts
    # =========================================================================

    def record_publish_attempt(self, attempt: PublishAttemptModel) -> PublishAttemptModel:
        """Log an Instagram publication attempt."""
        with get_connection(self.db_path) as conn:
            cur = conn.execute(
                """
                INSERT INTO publish_attempts (post_id, attempt_time, status, response_payload, error_message)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    attempt.post_id,
                    attempt.attempt_time,
                    attempt.status,
                    attempt.response_payload,
                    attempt.error_message,
                ),
            )
            attempt.id = cur.lastrowid
        return attempt

    # =========================================================================
    # Settings & Dashboard
    # =========================================================================

    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Retrieve system setting value."""
        with get_connection(self.db_path) as conn:
            row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
            if row:
                return row["value"]
            return default

    def set_setting(self, key: str, value: str) -> None:
        """Upsert system setting value."""
        now = datetime.now(timezone.utc).isoformat()
        with get_connection(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO settings (key, value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at
                """,
                (key, value, now),
            )

    def get_dashboard_stats(self) -> dict[str, int]:
        """Compute aggregate counts for dashboard."""
        with get_connection(self.db_path) as conn:
            total_topics = conn.execute("SELECT COUNT(*) FROM topics").fetchone()[0]
            pending_topics = conn.execute("SELECT COUNT(*) FROM topics WHERE status = 'pending'").fetchone()[0]
            draft_posts = conn.execute("SELECT COUNT(*) FROM posts WHERE status = 'draft'").fetchone()[0]
            approved_posts = conn.execute("SELECT COUNT(*) FROM posts WHERE status = 'approved'").fetchone()[0]
            published_posts = conn.execute("SELECT COUNT(*) FROM posts WHERE status = 'published'").fetchone()[0]
            failed_posts = conn.execute("SELECT COUNT(*) FROM posts WHERE status = 'failed'").fetchone()[0]

            return {
                "total_topics": total_topics,
                "pending_topics": pending_topics,
                "draft_posts": draft_posts,
                "approved_posts": approved_posts,
                "published_posts": published_posts,
                "failed_posts": failed_posts,
            }
