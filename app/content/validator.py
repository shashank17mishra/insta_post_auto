"""Content validation service ensuring note quality before rendering."""

from typing import Tuple
from app.content.schemas import NotePostContent


def validate_latex_formula(formula: str) -> Tuple[bool, str]:
    """Basic structural validation for LaTeX/mathtext formula string."""
    if not formula:
        return True, ""
    # Check balanced braces
    if formula.count("{") != formula.count("}"):
        return False, f"Unbalanced curly braces in formula: '{formula}'"
    if formula.count("(") != formula.count(")"):
        return False, f"Unbalanced parentheses in formula: '{formula}'"
    if formula.count("[") != formula.count("]"):
        return False, f"Unbalanced brackets in formula: '{formula}'"
    return True, ""


def validate_note_content(content: NotePostContent) -> Tuple[bool, list[str]]:
    """Validate educational content against visual and semantic guidelines."""
    errors: list[str] = []

    if not content.topic or len(content.topic.strip()) < 2:
        errors.append("Topic is missing or too short.")

    if not content.title or len(content.title.strip()) < 3:
        errors.append("Title is missing or too short.")

    if not content.pages:
        errors.append("Content must have at least 1 page.")
    elif len(content.pages) > 10:
        errors.append(f"Content has {len(content.pages)} pages, maximum recommended is 10.")

    for i, page in enumerate(content.pages, start=1):
        if not page.heading:
            errors.append(f"Page {i} is missing a heading.")
        if not page.sections:
            errors.append(f"Page {i} has no sections.")

        for j, sec in enumerate(page.sections, start=1):
            if not sec.heading and not sec.body and not sec.formula and not sec.code:
                errors.append(f"Page {i}, section {j} is completely empty.")

            if sec.formula:
                valid_formula, formula_err = validate_latex_formula(sec.formula)
                if not valid_formula:
                    errors.append(f"Page {i}, section {j}: {formula_err}")

            if sec.code and len(sec.code) > 800:
                errors.append(f"Page {i}, section {j} code snippet exceeds 800 characters (will not fit).")

    if not content.caption or len(content.caption.strip()) < 10:
        errors.append("Caption is missing or too short.")

    if content.hashtags:
        for tag in content.hashtags:
            if not tag.startswith("#"):
                errors.append(f"Hashtag '{tag}' must start with '#'.")

    return len(errors) == 0, errors
