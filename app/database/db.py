"""SQLite database connection and initialization."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator
from app.config import settings
from app.logging_config import logger

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS topics (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    difficulty TEXT NOT NULL DEFAULT 'beginner',
    status TEXT NOT NULL DEFAULT 'pending',
    priority INTEGER NOT NULL DEFAULT 50,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id TEXT NOT NULL,
    title TEXT NOT NULL,
    caption TEXT NOT NULL,
    hashtags TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'draft',
    content_hash TEXT NOT NULL DEFAULT '',
    dry_run INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    approved_at TEXT,
    published_at TEXT,
    instagram_media_id TEXT,
    error TEXT,
    FOREIGN KEY(topic_id) REFERENCES topics(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS pages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    page_number INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    width INTEGER NOT NULL DEFAULT 1080,
    height INTEGER NOT NULL DEFAULT 1350,
    created_at TEXT NOT NULL,
    FOREIGN KEY(post_id) REFERENCES posts(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS publish_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    attempt_time TEXT NOT NULL,
    status TEXT NOT NULL,
    response_payload TEXT,
    error_message TEXT,
    FOREIGN KEY(post_id) REFERENCES posts(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_topics_status_priority ON topics(status, priority DESC);
CREATE INDEX IF NOT EXISTS idx_posts_status ON posts(status);
CREATE INDEX IF NOT EXISTS idx_posts_content_hash ON posts(content_hash);
CREATE INDEX IF NOT EXISTS idx_pages_post_id ON pages(post_id, page_number);
"""


def get_db_path() -> Path:
    """Return configured database path and ensure directory exists."""
    path = settings.database_path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def init_db(db_path: Path = None) -> None:
    """Initialize database schemas and apply PRAGMAs."""
    path = db_path or get_db_path()
    with sqlite3.connect(path) as conn:
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.executescript(SCHEMA_SQL)
        conn.commit()
    logger.info(f"Database initialized at {path}")


@contextmanager
def get_connection(db_path: Path = None) -> Generator[sqlite3.Connection, None, None]:
    """Provide a transactional database connection."""
    path = db_path or get_db_path()
    conn = sqlite3.connect(path, timeout=20.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error, rolled back transaction: {e}")
        raise
    finally:
        conn.close()
