"""Computer Science Theory specialized template renderer."""

from PIL import Image, ImageDraw
from app.content.schemas import PageContent
from app.renderer.canvas import DESIGN_TOKENS
from app.renderer.decorations import (
    draw_bullet_points,
    draw_callout_note,
    draw_heading_with_underline,
)
from app.renderer.typography import font_manager


def render_cs_theory_page(canvas: Image.Image, page_content: PageContent) -> Image.Image:
    """Render a Computer Science Theory note page with tables and structured lists."""
    draw = ImageDraw.Draw(canvas)
    x = DESIGN_TOKENS["content_x_start"]
    y = DESIGN_TOKENS["content_y_start"]
    max_w = DESIGN_TOKENS["content_x_end"] - x

    body_font = font_manager.get_body_font(size=26)

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

        # 3. Comparison Table if present
        if sec.table_headers and sec.table_rows:
            table_h = _draw_comparison_table(draw, x, y, sec.table_headers, sec.table_rows, max_w)
            y += table_h + 12

        # 4. Bullet Points
        if sec.bullet_points:
            b_h = draw_bullet_points(draw, x + 8, y, sec.bullet_points, max_w - 8)
            y += b_h + 8

        # 5. Callout / Exam tip
        if sec.callout_text:
            note_type = sec.callout_type or "note"
            c_h = draw_callout_note(draw, x, y, note_type, sec.callout_text, max_w)
            y += c_h + 8

        y += 18

    return canvas


def _draw_comparison_table(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    headers: list[str],
    rows: list[list[str]],
    max_w: int,
) -> int:
    """Draw a clean handwritten-style comparison table."""
    font = font_manager.get_body_font(size=24)
    header_font = font_manager.get_heading_font(size=25)

    n_cols = len(headers)
    col_w = max_w // n_cols
    row_pad = 12

    # Measure row heights
    row_heights = [50]  # Header height
    for r in rows:
        max_lines = 1
        for cell in r:
            lines = font_manager.wrap_text(str(cell), font, col_w - 24, draw)
            if len(lines) > max_lines:
                max_lines = len(lines)
        row_heights.append(max_lines * 32 + row_pad * 2)

    total_h = sum(row_heights)

    # Outer table border
    draw.rectangle([x, y, x + max_w, y + total_h], outline=DESIGN_TOKENS["box_border"], width=2)

    # Header background fill
    draw.rectangle([x, y, x + max_w, y + row_heights[0]], fill=(241, 245, 249))
    draw.line([(x, y + row_heights[0]), (x + max_w, y + row_heights[0])], fill=DESIGN_TOKENS["box_border"], width=2)

    # Header text
    for i, h in enumerate(headers):
        draw.text((x + i * col_w + 14, y + 10), h, fill=DESIGN_TOKENS["ink_heading_title"], font=header_font)
        if i > 0:
            draw.line([(x + i * col_w, y), (x + i * col_w, y + total_h)], fill=DESIGN_TOKENS["box_border"], width=1)

    # Rows
    curr_y = y + row_heights[0]
    for r_idx, r in enumerate(rows):
        h = row_heights[r_idx + 1]
        for c_idx, cell in enumerate(r):
            if c_idx >= n_cols:
                break
            cell_lines = font_manager.wrap_text(str(cell), font, col_w - 24, draw)
            text_y = curr_y + row_pad
            for line_str in cell_lines:
                draw.text((x + c_idx * col_w + 14, text_y), line_str, fill=DESIGN_TOKENS["ink_body"], font=font)
                text_y += 30

        curr_y += h
        if r_idx < len(rows) - 1:
            draw.line([(x, curr_y), (x + max_w, curr_y)], fill=DESIGN_TOKENS["box_border"], width=1)

    return total_h
