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
        """Fetch the highest priority topic ready for generation, auto-replenishing via AI if empty."""
        topic = self.repo.get_next_pending_topic(category=category)
        if topic:
            logger.info(f"Selected next pending topic: '{topic.name}' [{topic.category}] (ID: {topic.id})")
            return topic

        # Auto-replenish if no pending topics remain
        logger.info("No pending topics found. Asking Gemini to discover new educational topics...")
        self._replenish_topics_with_ai(category)
        topic = self.repo.get_next_pending_topic(category=category)
        if topic:
            logger.info(f"Selected newly discovered topic: '{topic.name}' [{topic.category}]")
        return topic

    def _replenish_topics_with_ai(self, category: Optional[str] = None) -> None:
        """Use Gemini to brainstorm 5 fresh, high-yield educational topics."""
        from app.ai.gemini_client import GeminiClient
        from app.database.models import TopicStatus
        import uuid

        client = GeminiClient()
        if not client.is_configured():
            logger.warning("Gemini API not configured to auto-replenish topics.")
            return

        cat_prompt = category or "Computer Science, Algorithms, Data Science, or Mathematics"
        prompt = (
            f"Generate 5 high-yield, engaging educational topics for study notes in {cat_prompt}. "
            "Return JSON in this format: "
            '{"topics": [{"name": "Topic Name", "category": "Category", "difficulty": "beginner"}]}'
        )

        try:
            res = client.generate_json(prompt)
            topics_list = res.get("topics", [])
            for t in topics_list:
                name = t.get("name", "").strip()
                if not name:
                    continue
                topic_id = name.lower().replace(" ", "-").replace("(", "").replace(")", "")[:40]
                new_topic = TopicModel(
                    id=f"{topic_id}-{uuid.uuid4().hex[:4]}",
                    name=name,
                    category=t.get("category", category or "General"),
                    difficulty=t.get("difficulty", "beginner"),
                    status=TopicStatus.PENDING,
                    priority=50,
                )
                self.repo.create_topic(new_topic)
            logger.info(f"Successfully auto-discovered and added {len(topics_list)} new topics.")
        except Exception as e:
            logger.error(f"Failed to auto-replenish topics via AI: {e}")

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
