"""Pydantic schemas for structured educational note content."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class PageType(str, Enum):
    CONCEPT = "concept"
    FORMULA = "formula"
    EXAMPLE = "example"
    COMPARISON = "comparison"
    SUMMARY = "summary"
    PRACTICE = "practice"


class ContentSection(BaseModel):
    """An individual section within a note page."""
    heading: str = Field(..., description="Section title, e.g. '39. GROUP BY Clause' or '★ Cayley-Hamilton Theorem'")
    body: str = Field(default="", description="Concise handwritten-style explanation")
    formula: Optional[str] = Field(default=None, description=r"LaTeX / Mathtext expression if applicable, e.g. '|A - \lambda I| = 0'")
    code: Optional[str] = Field(default=None, description="Clean SQL, Python, or pseudo-code snippet")
    side_annotation: Optional[str] = Field(default=None, description="Short handwritten comment next to code/formula, e.g. '# Groups employees by dept'")
    bullet_points: Optional[list[str]] = Field(default_factory=list, description="Key points or properties")
    callout_type: Optional[str] = Field(default=None, description="Type: 'note', 'important', 'exam_tip', 'memory_trick', or 'benefit'")
    callout_text: Optional[str] = Field(default=None, description="Highlight or callout body")
    table_headers: Optional[list[str]] = Field(default=None, description="Table column headers for comparisons")
    table_rows: Optional[list[list[str]]] = Field(default=None, description="Table rows")


class PageContent(BaseModel):
    """Content for an individual Instagram carousel page (1080x1350)."""
    page_number: int = Field(default=1, description="Sequential 1-based page number")
    page_type: str = Field(default="concept", description="Type of content layout")
    heading: str = Field(..., description="Main page title / header")
    sections: list[ContentSection] = Field(default_factory=list, description="1 to 4 sections fitting on the page")


class NotePostContent(BaseModel):
    """Complete structured content for an educational Instagram post/carousel."""
    topic: str = Field(..., description="Topic name")
    subject: str = Field(..., description="Category / subject area (e.g. SQL, Mathematics, DBMS)")
    difficulty: str = Field(default="beginner", description="Difficulty level: beginner, intermediate, advanced")
    title: str = Field(..., description="Post title")
    subtitle: str = Field(default="", description="Subtitle or focus statement")
    pages: list[PageContent] = Field(..., min_length=1, max_length=10, description="List of carousel pages")
    key_takeaways: list[str] = Field(default_factory=list, description="Quick summary bullets")
    exam_tip: str = Field(default="", description="High-yield exam or interview tip")
    caption: str = Field(..., description="Ready-to-publish Instagram caption")
    hashtags: list[str] = Field(default_factory=list, description="5 to 15 targeted hashtags")
