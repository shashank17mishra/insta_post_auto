"""Post management and review API routes."""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from app.database.repository import Repository
from app.services.generation_service import generation_service
from app.services.publishing_service import publishing_service

router = APIRouter(prefix="/api", tags=["Posts"])
repo = Repository()


class RejectRequest(BaseModel):
    reason: Optional[str] = "Rejected by user"


@router.get("/posts")
def list_posts(status: Optional[str] = Query(None), limit: int = Query(50, ge=1, le=200)):
    """List posts filtered by status (draft, approved, published, failed)."""
    posts = repo.list_posts(status=status, limit=limit)
    result = []
    for p in posts:
        pages = repo.get_pages_for_post(p.id)
        d = p.model_dump()
        d["pages"] = [page.model_dump() for page in pages]
        result.append(d)
    return {"posts": result, "count": len(result)}


@router.get("/posts/{post_id}")
def get_post_detail(post_id: int):
    """Fetch complete post details including slide pages."""
    post = repo.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail=f"Post #{post_id} not found.")

    pages = repo.get_pages_for_post(post_id)
    d = post.model_dump()
    d["pages"] = [page.model_dump() for page in pages]
    return d


@router.post("/posts/{post_id}/approve")
def approve_post(post_id: int):
    """Approve a draft post for publication."""
    success, msg = publishing_service.approve_post(post_id)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg, "post_id": post_id, "status": "approved"}


@router.post("/posts/{post_id}/reject")
def reject_post(post_id: int, req: Optional[RejectRequest] = None):
    """Reject a draft post."""
    reason = req.reason if req else "Rejected by user"
    success, msg = publishing_service.reject_post(post_id, reason=reason)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg, "post_id": post_id, "status": "rejected"}


@router.post("/posts/{post_id}/regenerate")
def regenerate_post(post_id: int):
    """Regenerate notes for the topic of an existing post."""
    post = repo.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail=f"Post #{post_id} not found.")

    topic = repo.get_topic(post.topic_id)
    topic_name = topic.name if topic else post.topic_id

    new_post, errors = generation_service.generate_for_topic(
        topic_identifier=topic_name,
        force_mock=False,
    )
    if not new_post:
        raise HTTPException(status_code=400, detail={"message": "Regeneration failed", "errors": errors})

    return {
        "message": "Post regenerated successfully",
        "old_post_id": post_id,
        "new_post_id": new_post.id,
        "title": new_post.title,
    }


@router.post("/posts/{post_id}/publish")
def publish_post(post_id: int, force: bool = Query(False)):
    """Publish an approved post to Instagram (respecting DRY_RUN)."""
    success, msg = publishing_service.publish_now(post_id, force=force)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg, "post_id": post_id, "status": "published"}
