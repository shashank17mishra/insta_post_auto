"""Topic selection service for automated and manual workflows."""

from typing import Optional
from app.database.models import TopicModel
from app.database.repository import Repository
from app.logging_config import logger


class TopicSelector:
    """Selects topics from the database for note generation."""

    def __init__(self, repository: Repository):
        self.repo = repository

    def get_next_topic(self, category: Optional[str] = None) -> Optional[TopicModel]:
        """Fetch the highest priority topic ready for generation."""
        topic = self.repo.get_next_pending_topic(category=category)
        if topic:
            logger.info(f"Selected next pending topic: '{topic.name}' [{topic.category}] (ID: {topic.id})")
        else:
            logger.warning("No pending topics found in database.")
        return topic

    def get_topic_by_id_or_name(self, identifier: str) -> Optional[TopicModel]:
        """Fetch topic by ID or exact name."""
        topic = self.repo.get_topic(identifier)
        if not topic:
            topic = self.repo.get_topic_by_name(identifier)
        return topic

    def list_categories(self) -> list[str]:
        """Get unique list of topic categories."""
        topics = self.repo.list_topics(limit=500)
        categories = sorted(list({t.category for t in topics}))
        return categories
