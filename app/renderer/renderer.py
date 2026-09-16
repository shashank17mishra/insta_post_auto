"""Master note renderer orchestrating canvas, templates, and page output."""

from pathlib import Path
from typing import Optional
from PIL import Image, ImageDraw
from app.content.schemas import NotePostContent, PageContent
from app.logging_config import logger
from app.renderer.canvas import DESIGN_TOKENS, create_notebook_canvas
from app.renderer.decorations import draw_circled_page_number
from app.renderer.templates.cs_theory import render_cs_theory_page
from app.renderer.templates.data_science import render_data_science_page
from app.renderer.templates.math import render_math_page
from app.renderer.templates.sql import render_sql_page
from app.renderer.typography import font_manager


class NoteRenderer:
    """Master rendering engine that produces 1080x1350 Instagram carousel notes."""

    def __init__(self, show_spiral: bool = True):
        self.show_spiral = show_spiral

    def render_post(
        self,
        content: NotePostContent,
        output_dir: Optional[Path] = None,
    ) -> list[Image.Image]:
        """Render all pages for a study note post into PIL Images (1080x1350)."""
        logger.info(f"Rendering note post '{content.title}' ({len(content.pages)} pages)...")
        rendered_images: list[Image.Image] = []

        total_pages = len(content.pages)
        for idx, page in enumerate(content.pages, start=1):
            page_img = self.render_single_page(
                page_content=page,
                subject=content.subject,
                page_num=idx,
                total_pages=total_pages,
            )
            rendered_images.append(page_img)

        # Save to output_dir if specified
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
            for idx, img in enumerate(rendered_images, start=1):
                img_path = output_dir / f"page_{idx:02d}.png"
                img.save(img_path, format="PNG", optimize=True)
                logger.info(f"Saved rendered page to {img_path}")

        return rendered_images

    def render_single_page(
        self,
        page_content: PageContent,
        subject: str,
        page_num: int,
        total_pages: int,
    ) -> Image.Image:
        """Render an individual 1080x1350 carousel note page."""
        # 1. Base notebook paper canvas
        canvas = create_notebook_canvas(
            width=DESIGN_TOKENS["width"],
            height=DESIGN_TOKENS["height"],
            show_spiral=self.show_spiral,
            show_ruled_lines=True,
            show_margin_line=True,
        )

        # 2. Select appropriate domain template
        subj_lower = subject.lower()
        if "sql" in subj_lower or "dbms" in subj_lower or "database" in subj_lower:
            render_sql_page(canvas, page_content)
        elif "math" in subj_lower or "algebra" in subj_lower or "calculus" in subj_lower:
            render_math_page(canvas, page_content)
        elif "data" in subj_lower or "machine" in subj_lower or "ml" in subj_lower or "ai" in subj_lower:
            render_data_science_page(canvas, page_content)
        else:
            render_cs_theory_page(canvas, page_content)

        # 3. Add Circled Page Number at bottom right (placed cleanly on margin)
        draw = ImageDraw.Draw(canvas)
        draw_circled_page_number(
            draw=draw,
            page_num=page_num,
            x=DESIGN_TOKENS["content_x_end"] - 30,
            y=1308,
            radius=24,
        )

        # 4. Add subtle brand footer on bottom left
        footer_font = font_manager.get_annotation_font(size=20)
        draw.text(
            (DESIGN_TOKENS["content_x_start"], 1300),
            f"StudyNotes  •  {subject}",
            fill=(148, 163, 184),
            font=footer_font,
        )

        return canvas


# Global renderer instance
note_renderer = NoteRenderer()
