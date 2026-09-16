"""SQL and Database specialized template renderer matching reference style."""

from PIL import Image, ImageDraw
from app.content.schemas import PageContent
from app.renderer.canvas import DESIGN_TOKENS
from app.renderer.decorations import (
    draw_callout_note,
    draw_code_box_with_annotation,
    draw_heading_with_underline,
)
from app.renderer.typography import font_manager


def render_sql_page(canvas: Image.Image, page_content: PageContent) -> Image.Image:
    """Render an SQL note page with code blocks and side annotations."""
    draw = ImageDraw.Draw(canvas)
    x = DESIGN_TOKENS["content_x_start"]
    y = DESIGN_TOKENS["content_y_start"] - 15  # Start slightly higher for 4 sections
    max_w = DESIGN_TOKENS["content_x_end"] - x

    body_font = font_manager.get_body_font(size=24)
    example_font = font_manager.get_annotation_font(size=23)

    for sec in page_content.sections:
        # Check available vertical space
        if y > DESIGN_TOKENS["content_y_end"] - 90:
            break

        # 1. Heading with red underline
        h_h = draw_heading_with_underline(draw, x, y, sec.heading)
        y += h_h + 4

        # 2. Body explanation text
        if sec.body:
            clean_body = font_manager.clean_inline_math(sec.body)
            lines = font_manager.wrap_text(clean_body, body_font, max_w, draw)
            line_h = draw.textbbox((0, 0), "Ag", font=body_font)[3] + 6
            for line_str in lines:
                draw.text((x, y), line_str, fill=DESIGN_TOKENS["ink_body"], font=body_font)
                y += line_h
            y += 2

        # 3. Example label & Code box with side annotation
        if sec.code:
            draw.text((x, y), "Example:", fill=DESIGN_TOKENS["ink_heading_num"], font=example_font)
            y += draw.textbbox((0, 0), "Example:", font=example_font)[3] + 4

            box_h = draw_code_box_with_annotation(
                draw=draw,
                x=x + 4,
                y=y,
                code_text=sec.code,
                side_annotation=sec.side_annotation,
                max_total_width=max_w - 4,
            )
            y += box_h + 4

        # 4. Callout / Note
        if sec.callout_text:
            note_type = sec.callout_type or "note"
            c_h = draw_callout_note(draw, x, y, note_type, sec.callout_text, max_w)
            y += c_h + 4

        # Spacing between sections
        y += 12

    return canvas
