"""Mathematics specialized template renderer for formulas and theorems."""

from PIL import Image, ImageDraw
from app.content.schemas import PageContent
from app.renderer.canvas import DESIGN_TOKENS
from app.renderer.decorations import (
    draw_bullet_points,
    draw_callout_note,
    draw_heading_with_underline,
)
from app.renderer.formulas import render_formula_image
from app.renderer.typography import font_manager


def render_math_page(canvas: Image.Image, page_content: PageContent) -> Image.Image:
    """Render a mathematics note page with LaTeX formulas and boxed equations."""
    draw = ImageDraw.Draw(canvas)
    x = DESIGN_TOKENS["content_x_start"]
    y = DESIGN_TOKENS["content_y_start"]
    max_w = DESIGN_TOKENS["content_x_end"] - x

    body_font = font_manager.get_body_font(size=27)
    annot_font = font_manager.get_annotation_font(size=23)

    for sec in page_content.sections:
        if y > DESIGN_TOKENS["content_y_end"] - 120:
            break

        # 1. Section Title
        h_h = draw_heading_with_underline(draw, x, y, sec.heading)
        y += h_h + 10

        # 2. Body
        if sec.body:
            lines = font_manager.wrap_text(sec.body, body_font, max_w, draw)
            line_h = draw.textbbox((0, 0), "Ag", font=body_font)[3] + 10
            for line_str in lines:
                draw.text((x, y), line_str, fill=DESIGN_TOKENS["ink_body"], font=body_font)
                y += line_h
            y += 8

        # 3. Formula block (rendered via Mathtext/LaTeX engine)
        if sec.formula:
            formula_img = render_formula_image(sec.formula, fontsize=24, color="#102A43", max_width=max_w - 40)
            if formula_img:
                # Place formula inside a clean rounded formula container
                f_pad_x = 30
                f_pad_y = 16
                box_w = min(max_w, formula_img.width + (f_pad_x * 2))
                box_h = formula_img.height + (f_pad_y * 2)

                draw.rounded_rectangle(
                    [x + 10, y, x + 10 + box_w, y + box_h],
                    radius=8,
                    fill=DESIGN_TOKENS["box_fill"],
                    outline=DESIGN_TOKENS["box_border"],
                    width=2,
                )
                # Paste formula image with alpha composite
                canvas.paste(formula_img, (x + 10 + f_pad_x, y + f_pad_y), formula_img)

                # Side annotation next to formula box if present
                if sec.side_annotation:
                    annot_x = x + 10 + box_w + 20
                    annot_w = max_w - (box_w + 30)
                    annot_lines = font_manager.wrap_text(sec.side_annotation, annot_font, annot_w, draw)
                    annot_y = y + max(4, (box_h - len(annot_lines) * 28) // 2)
                    for al in annot_lines:
                        draw.text((annot_x, annot_y), al, fill=DESIGN_TOKENS["ink_annotation"], font=annot_font)
                        annot_y += 28

                y += box_h + 12

        # 4. Bullet Points
        if sec.bullet_points:
            b_h = draw_bullet_points(draw, x + 8, y, sec.bullet_points, max_w - 8)
            y += b_h + 8

        # 5. Callout note
        if sec.callout_text:
            note_type = sec.callout_type or "note"
            c_h = draw_callout_note(draw, x, y, note_type, sec.callout_text, max_w)
            y += c_h + 8

        y += 18

    return canvas
