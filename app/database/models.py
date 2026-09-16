"""Database model definitions and schemas."""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


def utc_now_str() -> str:
    """Return ISO format string of current UTC time."""
    return datetime.now(timezone.utc).isoformat()


class TopicStatus(str, Enum):
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class PostStatus(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    REJECTED = "rejected"
    PUBLISHED = "published"
    FAILED = "failed"


class TopicModel(BaseModel):
    """Topic representation."""
    id: str
    name: str
    category: str
    difficulty: str = "beginner"
    status: TopicStatus = TopicStatus.PENDING
    priority: int = 50
    created_at: str = Field(default_factory=utc_now_str)
    updated_at: str = Field(default_factory=utc_now_str)


class PostModel(BaseModel):
    """Generated note post representation."""
    id: int = 0
    topic_id: str
    title: str
    caption: str
    hashtags: str = ""  # Space or comma-separated hashtags
    status: PostStatus = PostStatus.DRAFT
    content_hash: str = ""
    dry_run: bool = True
    created_at: str = Field(default_factory=utc_now_str)
    approved_at: Optional[str] = None
    published_at: Optional[str] = None
    instagram_media_id: Optional[str] = None
    error: Optional[str] = None


class PageModel(BaseModel):
    """Individual carousel slide representation."""
    id: int = 0
    post_id: int
    page_number: int
    file_path: str
    width: int = 1080
    height: int = 1350
    created_at: str = Field(default_factory=utc_now_str)


class PublishAttemptModel(BaseModel):
    """Record of an Instagram publish attempt."""
    id: int = 0
    post_id: int
    attempt_time: str = Field(default_factory=utc_now_str)
    status: str  # SUCCESS, FAILED, DRY_RUN
    response_payload: Optional[str] = None
    error_message: Optional[str] = None


class SettingModel(BaseModel):
    """Key-value system setting."""
    key: str
    value: str
    updated_at: str = Field(default_factory=utc_now_str)
