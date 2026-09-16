"""Tests for content validation, schemas, and deduplication."""

from app.ai.content_generator import ContentGenerator
from app.content.deduplicator import compute_post_hash, normalize_topic_name
from app.content.schemas import ContentSection, NotePostContent, PageContent, PageType
from app.content.validator import validate_latex_formula, validate_note_content


def test_latex_formula_validator():
    """Verify formula brace balance checking."""
    valid, _ = validate_latex_formula(r"|A - \lambda I| = 0")
    assert valid is True

    valid_unbalanced, err = validate_latex_formula(r"\frac{a}{b")
    assert valid_unbalanced is False
    assert "Unbalanced" in err


def test_note_content_validation():
    """Verify validation of complete NotePostContent."""
    valid_content = NotePostContent(
        topic="Binary Search",
        subject="Algorithms",
        difficulty="beginner",
        title="Binary Search Algorithm",
        pages=[
            PageContent(
                page_number=1,
                page_type=PageType.CONCEPT,
                heading="Overview",
                sections=[
                    ContentSection(
                        heading="1. Definition",
                        body="Search in sorted array with O(log n) time.",
                        bullet_points=["Requires sorted input", "Halves search interval"],
                    )
                ],
            )
        ],
        caption="Master Binary Search! #Algorithms #BTech",
        hashtags=["#Algorithms", "#BTech"],
    )

    is_valid, errors = validate_note_content(valid_content)
    assert is_valid is True
    assert len(errors) == 0


def test_invalid_content_detected():
    """Verify that empty or malformed content fails validation."""
    import pytest
    from pydantic import ValidationError

    # 1. Pydantic requires at least 1 page
    with pytest.raises(ValidationError):
        NotePostContent(
            topic="",
            subject="",
            title="",
            pages=[],
            caption="",
        )

    # 2. validate_note_content catches missing headings/bodies
    empty_content = NotePostContent(
        topic="A",  # too short
        subject="X",
        title="B",  # too short
        pages=[
            PageContent(
                page_number=1,
                page_type=PageType.CONCEPT,
                heading="",  # missing heading
                sections=[
                    ContentSection(
                        heading="",
                        body="",
                    )
                ],
            )
        ],
        caption="Short",  # too short
    )
    is_valid, errors = validate_note_content(empty_content)
    assert is_valid is False
    assert len(errors) > 0


def test_content_hashing_consistency():
    """Verify that deterministic content hash produces identical output for identical content."""
    gen = ContentGenerator()
    c1 = gen.generate_study_note("SQL GROUP BY Clause", "SQL", force_mock=True)
    c2 = gen.generate_study_note("SQL GROUP BY Clause", "SQL", force_mock=True)

    h1 = compute_post_hash(c1)
    h2 = compute_post_hash(c2)
    assert h1 == h2
    assert len(h1) == 64  # SHA-256 length


def test_topic_normalization():
    """Verify that topic normalization handles case and punctuation."""
    norm1 = normalize_topic_name("SQL GROUP BY Clause!")
    norm2 = normalize_topic_name("sql  group  by  clause")
    assert norm1 == norm2
