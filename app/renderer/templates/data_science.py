"""Data Science & Machine Learning specialized template renderer."""

from PIL import Image, ImageDraw
from app.content.schemas import PageContent
from app.renderer.canvas import DESIGN_TOKENS
from app.renderer.decorations import (
    draw_bullet_points,
    draw_callout_note,
    draw_code_box_with_annotation,
    draw_heading_with_underline,
)
from app.renderer.formulas import render_formula_image
from app.renderer.typography import font_manager


def render_data_science_page(canvas: Image.Image, page_content: PageContent) -> Image.Image:
    """Render a Data Science note page with ML equations and concept cards."""
    draw = ImageDraw.Draw(canvas)
    x = DESIGN_TOKENS["content_x_start"]
    y = DESIGN_TOKENS["content_y_start"]
    max_w = DESIGN_TOKENS["content_x_end"] - x

    body_font = font_manager.get_body_font(size=26)

    for sec in page_content.sections:
        if y > DESIGN_TOKENS["content_y_end"] - 120:
            break

        # 1. Heading
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

        # 3. Formula if present
        if sec.formula:
            f_img = render_formula_image(sec.formula, fontsize=24, max_width=max_w - 40)
            if f_img:
                f_pad = 16
                box_w = min(max_w, f_img.width + (f_pad * 2))
                box_h = f_img.height + (f_pad * 2)

                draw.rounded_rectangle(
                    [x + 10, y, x + 10 + box_w, y + box_h],
                    radius=8,
                    fill=DESIGN_TOKENS["box_fill"],
                    outline=DESIGN_TOKENS["box_border"],
                    width=2,
                )
                canvas.paste(f_img, (x + 10 + f_pad, y + f_pad), f_img)
                y += box_h + 12

        # 4. Code snippet if present
        if sec.code:
            box_h = draw_code_box_with_annotation(
                draw=draw,
                x=x + 8,
                y=y,
                code_text=sec.code,
                side_annotation=sec.side_annotation,
                max_total_width=max_w - 8,
            )
            y += box_h + 10

        # 5. Bullet points
        if sec.bullet_points:
            b_h = draw_bullet_points(draw, x + 8, y, sec.bullet_points, max_w - 8)
            y += b_h + 8

        # 6. Callout
        if sec.callout_text:
            note_type = sec.callout_type or "note"
            c_h = draw_callout_note(draw, x, y, note_type, sec.callout_text, max_w)
            y += c_h + 8

        y += 18

    return canvas
