"""Generation trigger API routes."""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from app.services.generation_service import generation_service

router = APIRouter(prefix="/api", tags=["Generation"])


class GenerateRequest(BaseModel):
    category: Optional[str] = None
    force_mock: bool = False


@router.post("/generate/next")
def generate_next_topic(req: Optional[GenerateRequest] = None):
    """Generate notes for the next pending topic in priority queue."""
    category = req.category if req else None
    force_mock = req.force_mock if req else False

    post, errors = generation_service.generate_for_topic(
        category=category,
        force_mock=force_mock,
    )
    if not post:
        raise HTTPException(status_code=400, detail={"message": "Generation failed", "errors": errors})

    return {
        "message": "Note post generated successfully",
        "post_id": post.id,
        "title": post.title,
        "status": post.status.value,
        "errors": errors,
    }


@router.post("/generate/{topic_id}")
def generate_specific_topic(topic_id: str, force_mock: bool = Query(False)):
    """Generate notes for a specific topic ID or title."""
    post, errors = generation_service.generate_for_topic(
        topic_identifier=topic_id,
        force_mock=force_mock,
    )
    if not post:
        raise HTTPException(status_code=400, detail={"message": "Generation failed", "errors": errors})

    return {
        "message": "Note post generated successfully",
        "post_id": post.id,
        "title": post.title,
        "status": post.status.value,
        "errors": errors,
    }
