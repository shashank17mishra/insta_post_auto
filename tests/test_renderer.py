"""Tests for note renderer, canvas, formulas, and visual quality."""

from pathlib import Path
from PIL import Image
from app.content.schemas import ContentSection, NotePostContent, PageContent, PageType
from app.renderer.canvas import create_notebook_canvas
from app.renderer.formulas import render_formula_image, render_matrix_box
from app.renderer.renderer import NoteRenderer
from app.services.quality_service import quality_service


def test_notebook_canvas_dimensions():
    """Verify that notebook canvas is created with exact 1080x1350 Instagram dimensions."""
    canvas = create_notebook_canvas(1080, 1350)
    assert canvas.size == (1080, 1350)
    assert canvas.mode == "RGB"


def test_formula_rendering_latex():
    """Verify that mathematical formulas render into transparent RGBA PIL images."""
    formula = r"|A - \lambda I| = 0"
    img = render_formula_image(formula)
    assert img is not None
    assert isinstance(img, Image.Image)
    assert img.mode == "RGBA"
    assert img.width > 0
    assert img.height > 0


def test_formula_rendering_polynomial():
    """Verify rendering of polynomial matrix equation A^2 - 4A + 3I = 0."""
    formula = "A^2 - 4A + 3I = 0"
    img = render_formula_image(formula)
    assert img is not None
    assert img.width > 0


def test_matrix_rendering():
    """Verify that matrix rendering produces aligned bracketed image."""
    rows = [["1", "2"], ["3", "4"]]
    img = render_matrix_box(rows, fontsize=20)
    assert img is not None
    assert img.width > 30
    assert img.height > 30


def test_renderer_end_to_end(tmp_path: Path):
    """Verify that NoteRenderer outputs valid 1080x1350 PNG files."""
    content = NotePostContent(
        topic="SQL GROUP BY Clause",
        subject="SQL",
        difficulty="beginner",
        title="SQL GROUP BY Clause",
        subtitle="Grouping rows with aggregate calculations",
        pages=[
            PageContent(
                page_number=1,
                page_type=PageType.CONCEPT,
                heading="39. GROUP BY Clause",
                sections=[
                    ContentSection(
                        heading="39. GROUP BY Clause",
                        body="GROUP BY clause is used with aggregate functions.",
                        code="SELECT department_id, COUNT(*)\nFROM employees\nGROUP BY department_id;",
                        side_annotation="# Count employees",
                    )
                ],
            )
        ],
        caption="Sample caption #SQL",
        hashtags=["#SQL"],
    )

    renderer = NoteRenderer()
    images = renderer.render_post(content, output_dir=tmp_path)
    assert len(images) == 1
    assert images[0].size == (1080, 1350)

    # Verify saved file on disk
    saved_file = tmp_path / "page_01.png"
    assert saved_file.exists()

    # Verify via quality service
    valid, issues = quality_service.validate_rendered_page(saved_file)
    assert valid is True
    assert len(issues) == 0
