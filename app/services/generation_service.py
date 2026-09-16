"""Complete generation pipeline orchestrator."""

from typing import Optional, Tuple
from app.ai.caption_generator import CaptionGenerator
from app.ai.content_generator import ContentGenerator
from app.config import settings
from app.content.deduplicator import compute_post_hash, is_topic_already_published
from app.content.topic_selector import TopicSelector
from app.database.models import PageModel, PostModel, PostStatus, TopicModel, TopicStatus
from app.database.repository import Repository
from app.logging_config import logger
from app.renderer.renderer import note_renderer
from app.services.quality_service import quality_service
from app.utils.files import save_json


class GenerationService:
    """Orchestrates end-to-end generation from topic to validated draft notes."""

    def __init__(
        self,
        repository: Optional[Repository] = None,
        content_generator: Optional[ContentGenerator] = None,
    ):
        self.repo = repository or Repository()
        self.generator = content_generator or ContentGenerator()
        self.topic_selector = TopicSelector(self.repo)

    def generate_for_topic(
        self,
        topic_identifier: Optional[str] = None,
        category: Optional[str] = None,
        force_mock: bool = False,
    ) -> Tuple[Optional[PostModel], list[str]]:
        """Run full generation pipeline for a topic identifier or the next pending topic."""
        # 1. Select Topic
        topic: Optional[TopicModel] = None
        if topic_identifier:
            topic = self.topic_selector.get_topic_by_id_or_name(topic_identifier)
            if not topic:
                # Create transient topic if not present
                topic_id = topic_identifier.lower().replace(" ", "-")
                topic = TopicModel(
                    id=topic_id,
                    name=topic_identifier,
                    category=category or "General",
                    difficulty="beginner",
                    status=TopicStatus.PENDING,
                )
                self.repo.create_topic(topic)
        else:
            topic = self.topic_selector.get_next_topic(category=category)

        if not topic:
            return None, ["No available topic found to generate."]

        logger.info(f"Starting generation pipeline for topic: '{topic.name}' [{topic.category}]")
        self.repo.update_topic_status(topic.id, TopicStatus.GENERATING)

        # 2. Check Deduplication
        if is_topic_already_published(self.repo, topic.id):
            msg = f"Topic '{topic.name}' is already published. Skipping duplicate generation."
            logger.warning(msg)
            return None, [msg]

        try:
            # 3. Content Generation
            note_content = self.generator.generate_study_note(
                topic=topic.name,
                category=topic.category,
                difficulty=topic.difficulty,
                force_mock=force_mock,
            )

            # 4. Compute Content Hash
            content_hash = compute_post_hash(note_content)

            # 5. Format Caption & Hashtags
            caption_text = CaptionGenerator.format_full_caption(note_content)
            hashtags_str = " ".join(note_content.hashtags)

            # 6. Create Initial Post Record in DB
            post = PostModel(
                topic_id=topic.id,
                title=note_content.title,
                caption=caption_text,
                hashtags=hashtags_str,
                status=PostStatus.DRAFT,
                content_hash=content_hash,
                dry_run=settings.dry_run,
            )
            post = self.repo.create_post(post)

            # 7. Render Images to Draft Folder
            draft_dir = settings.output_dir / "drafts" / str(post.id)
            draft_dir.mkdir(parents=True, exist_ok=True)

            rendered_imgs = note_renderer.render_post(note_content, output_dir=draft_dir)
            page_paths = [draft_dir / f"page_{i:02d}.png" for i in range(1, len(rendered_imgs) + 1)]

            # 8. Visual Quality Check
            is_valid_quality, quality_issues = quality_service.validate_carousel_post(
                content=note_content, page_paths=page_paths
            )
            if not is_valid_quality:
                error_msg = f"Quality control failed: {'; '.join(quality_issues)}"
                self.repo.update_post_status(post.id, PostStatus.FAILED, error=error_msg)
                self.repo.update_topic_status(topic.id, TopicStatus.FAILED)
                return post, quality_issues

            # 9. Register Pages in DB
            for idx, p_path in enumerate(page_paths, start=1):
                try:
                    rel_path = str(p_path.resolve().relative_to(settings.project_root.resolve())).replace("\\", "/")
                except Exception:
                    rel_path = str(p_path).replace("\\", "/")

                page_record = PageModel(
                    post_id=post.id,
                    page_number=idx,
                    file_path=rel_path,
                    width=settings.canvas_width,
                    height=settings.canvas_height,
                )
                self.repo.create_page(page_record)

            # 10. Save Metadata & Caption text on disk
            metadata = {
                "post_id": post.id,
                "topic_id": topic.id,
                "topic": topic.name,
                "category": topic.category,
                "title": note_content.title,
                "pages": [p.name for p in page_paths],
                "caption": caption_text,
                "hashtags": note_content.hashtags,
                "content_hash": content_hash,
                "created_at": post.created_at,
                "status": post.status.value,
            }
            save_json(metadata, draft_dir / "metadata.json")
            with open(draft_dir / "caption.txt", "w", encoding="utf-8") as f:
                f.write(caption_text)

            # 11. Mark Topic as Completed
            self.repo.update_topic_status(topic.id, TopicStatus.COMPLETED)
            logger.info(f"Successfully generated draft post #{post.id} with {len(page_paths)} pages.")

            return post, []

        except Exception as e:
            err = f"Pipeline execution failed for topic '{topic.name}': {e}"
            logger.error(err)
            self.repo.update_topic_status(topic.id, TopicStatus.FAILED)
            return None, [err]


# Global instance
generation_service = GenerationService()
