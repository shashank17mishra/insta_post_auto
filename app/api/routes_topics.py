"""Topic management API routes."""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from app.content.topic_selector import TopicSelector
from app.database.models import TopicModel, TopicStatus
from app.database.repository import Repository

router = APIRouter(prefix="/api", tags=["Topics"])
repo = Repository()
selector = TopicSelector(repo)


class CreateTopicRequest(BaseModel):
    id: Optional[str] = None
    name: str = Field(..., min_length=2, max_length=150)
    category: str = Field(..., min_length=2, max_length=60)
    difficulty: str = Field(default="beginner")
    priority: int = Field(default=50, ge=1, le=100)


@router.get("/topics")
def list_topics(
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """List topics from database with optional filters."""
    topics = repo.list_topics(category=category, status=status, limit=limit, offset=offset)
    return {"topics": [t.model_dump() for t in topics], "count": len(topics)}


@router.post("/topics")
def create_topic(req: CreateTopicRequest):
    """Register a new educational topic in the database."""
    topic_id = req.id or req.name.lower().replace(" ", "-")
    existing = repo.get_topic(topic_id)
    if existing:
        raise HTTPException(status_code=409, detail=f"Topic with ID '{topic_id}' already exists.")

    topic = TopicModel(
        id=topic_id,
        name=req.name,
        category=req.category,
        difficulty=req.difficulty,
        priority=req.priority,
        status=TopicStatus.PENDING,
    )
    saved = repo.create_topic(topic)
    return {"message": "Topic created successfully", "topic": saved.model_dump()}


@router.get("/categories")
def get_categories():
    """List all categories represented in topics."""
    return {"categories": selector.list_categories()}
