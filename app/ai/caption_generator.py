"""Instagram caption and hashtag generation utility."""

from app.content.schemas import NotePostContent


class CaptionGenerator:
    """Builds clean, high-engagement Instagram captions for study notes."""

    @staticmethod
    def format_full_caption(content: NotePostContent) -> str:
        """Combine note title, summary, exam tips, and hashtags into Instagram caption."""
        if content.caption and len(content.caption.strip()) > 30:
            caption = content.caption.strip()
        else:
            caption = f"📚 {content.title} | Revision Notes\n\n"
            if content.subtitle:
                caption += f"✨ {content.subtitle}\n\n"
            if content.key_takeaways:
                caption += "💡 Key Takeaways:\n"
                for item in content.key_takeaways[:3]:
                    caption += f"• {item}\n"
                caption += "\n"
            if content.exam_tip:
                caption += f"🎯 Exam Tip:\n{content.exam_tip}\n\n"
            caption += "Save this post for your technical interviews & exams! 🔖\n"

        # Ensure hashtags are included
        tags_str = " ".join(content.hashtags) if content.hashtags else "#StudyNotes #ComputerScience #BTech"
        if tags_str not in caption:
            caption = f"{caption}\n\n{tags_str}"

        return caption.strip()
