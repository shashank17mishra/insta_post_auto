"""Educational content generator using Gemini 3.8 Flash with offline fallbacks."""

from typing import Optional
from app.ai.gemini_client import GeminiClient
from app.ai.prompts import SYSTEM_PROMPT, TOPIC_PROMPT_TEMPLATE
from app.content.schemas import (
    ContentSection,
    NotePostContent,
    PageContent,
    PageType,
)
from app.content.validator import validate_note_content
from app.logging_config import logger


class ContentGenerator:
    """Generates structured educational study notes."""

    def __init__(self, gemini_client: Optional[GeminiClient] = None):
        self.client = gemini_client or GeminiClient()

    def generate_study_note(
        self,
        topic: str,
        category: str = "General",
        difficulty: str = "beginner",
        force_mock: bool = False,
    ) -> NotePostContent:
        """Generate validated study note content for a topic."""
        logger.info(f"Generating study note content for: '{topic}' ({category}, {difficulty})")

        # Use curated high-yield template if force_mock or Gemini API key is unconfigured
        if force_mock or not self.client.is_configured():
            logger.info("Using built-in curated educational template (mock/offline mode).")
            return self._generate_fallback_content(topic, category, difficulty)

        try:
            prompt = TOPIC_PROMPT_TEMPLATE.format(
                topic=topic,
                category=category,
                difficulty=difficulty,
            )
            raw_json = self.client.generate_json(
                prompt=prompt,
                system_instruction=SYSTEM_PROMPT,
            )
            note_content = NotePostContent.model_validate(raw_json)

            is_valid, errors = validate_note_content(note_content)
            if not is_valid:
                logger.warning(f"Content validation found issues: {errors}. Falling back to curated template.")
                return self._generate_fallback_content(topic, category, difficulty)

            logger.info(f"Successfully generated structured content with {len(note_content.pages)} pages.")
            return note_content

        except Exception as e:
            logger.error(f"Error calling Gemini for '{topic}': {e}. Falling back to curated template.")
            return self._generate_fallback_content(topic, category, difficulty)

    def _generate_fallback_content(
        self, topic: str, category: str, difficulty: str
    ) -> NotePostContent:
        """Return handcrafted, textbook-accurate templates for sample topics."""
        t_lower = topic.lower()

        # 1. SQL GROUP BY / CLAUSES (matching reference image)
        if "group by" in t_lower or "having" in t_lower or "sql" in t_lower:
            return NotePostContent(
                topic="SQL GROUP BY Clause",
                subject="SQL",
                difficulty="beginner",
                title="SQL Query Clauses & Grouping",
                subtitle="Mastering GROUP BY, HAVING, ORDER BY & TOP",
                pages=[
                    PageContent(
                        page_number=1,
                        page_type=PageType.CONCEPT,
                        heading="SQL Grouping & Filtering Guide",
                        sections=[
                            ContentSection(
                                heading="39. GROUP BY Clause",
                                body="GROUP BY clause is used with aggregate functions to group the result-set by one or more columns.",
                                code=(
                                    "SELECT department_id, COUNT(*) AS total_employees\n"
                                    "FROM employees\n"
                                    "GROUP BY department_id;"
                                ),
                                side_annotation="# Groups employees by department and counts total employees",
                                bullet_points=[],
                            ),
                            ContentSection(
                                heading="40. HAVING Clause",
                                body="HAVING clause is used to filter groups created by GROUP BY.",
                                code=(
                                    "SELECT department_id, COUNT(*) AS total_employees\n"
                                    "FROM employees\n"
                                    "GROUP BY department_id\n"
                                    "HAVING COUNT(*) > 5;"
                                ),
                                side_annotation="# Displays departments having more than 5 employees",
                                callout_type="note",
                                callout_text=(
                                    "WHERE filters rows before grouping.\n"
                                    "HAVING filters groups after grouping."
                                ),
                            ),
                        ],
                    ),
                    PageContent(
                        page_number=2,
                        page_type=PageType.CONCEPT,
                        heading="SQL Sorting & Limiting Guide",
                        sections=[
                            ContentSection(
                                heading="41. ORDER BY Clause",
                                body="ORDER BY clause is used to sort the result-set in ascending (ASC) or descending (DESC) order.",
                                code=(
                                    "SELECT name, salary\n"
                                    "FROM employees\n"
                                    "ORDER BY salary DESC;"
                                ),
                                side_annotation="# Sorts employees by salary in descending order",
                            ),
                            ContentSection(
                                heading="42. TOP Clause",
                                body="TOP clause is used to specify the number of rows to return from the result-set.",
                                code=(
                                    "SELECT TOP 5 name, salary\n"
                                    "FROM employees\n"
                                    "ORDER BY salary DESC;"
                                ),
                                side_annotation="# Returns top 5 highest salaries",
                                callout_type="note",
                                callout_text="TOP is specific to SQL Server (standard SQL uses LIMIT / FETCH).",
                            ),
                        ],
                    ),
                ],
                key_takeaways=[
                    "GROUP BY aggregates rows into summary rows.",
                    "WHERE cannot be used with aggregate functions; use HAVING instead.",
                    "ORDER BY is evaluated at the very end of SQL query processing.",
                ],
                exam_tip="GATE / Interview favorite: Remember the execution order: FROM -> WHERE -> GROUP BY -> HAVING -> SELECT -> ORDER BY.",
                caption=(
                    "📚 SQL Clauses Explained Simply!\n\n"
                    "Swipe to master GROUP BY, HAVING, ORDER BY, and TOP clauses with clean syntax and exam notes.\n\n"
                    "💡 Quick Rule:\n"
                    "• WHERE filters rows BEFORE grouping\n"
                    "• HAVING filters groups AFTER grouping\n\n"
                    "Save this post for quick revision before your technical interviews! 🔖\n\n"
                    "#SQL #DBMS #Database #BTech #ComputerScience #SoftwareEngineering #DataEngineering"
                ),
                hashtags=[
                    "#SQL",
                    "#DBMS",
                    "#Database",
                    "#BTech",
                    "#ComputerScience",
                    "#Programming",
                    "#DataEngineering",
                    "#CodingInterview",
                ],
            )

        # 2. CAYLEY-HAMILTON THEOREM & DIAGONALIZATION (matching reference math note)
        if "cayley" in t_lower or "eigen" in t_lower or "math" in str(category).lower():
            return NotePostContent(
                topic="Cayley-Hamilton Theorem",
                subject="Mathematics",
                difficulty="intermediate",
                title="Cayley-Hamilton Theorem & Diagonalization",
                subtitle="Engineering Mathematics & Linear Algebra",
                pages=[
                    PageContent(
                        page_number=1,
                        page_type=PageType.FORMULA,
                        heading="5. CAYLEY-HAMILTON THEOREM",
                        sections=[
                            ContentSection(
                                heading="★ Statement of the Theorem",
                                body="Every square matrix A satisfies its own characteristic equation.",
                                formula="|A - \\lambda I| = 0",
                                callout_type="important",
                                callout_text=(
                                    "If |A - \\lambda I| = 0 gives: \\lambda^n + c_1 \\lambda^{n-1} + \\dots + c_n = 0\n"
                                    "then matrix equation holds: A^n + c_1 A^{n-1} + \\dots + c_n I = 0"
                                ),
                                bullet_points=[
                                    "Allows direct calculation of matrix inverse A^{-1}",
                                    "Simplifies higher powers: A^4, A^8, A^k without repeated multiplication",
                                ],
                            ),
                            ContentSection(
                                heading="★ Verification Example",
                                body="For a 2x2 matrix with characteristic equation: \\lambda^2 - 4\\lambda + 3 = 0",
                                formula="A^2 - 4A + 3I = 0",
                                side_annotation="# Pre-multiply by A^{-1} to compute inverse directly!",
                                callout_type="note",
                                callout_text="3I = 4A - A^2  ==>  A^{-1} = \\frac{1}{3}(4I - A)",
                            ),
                        ],
                    ),
                    PageContent(
                        page_number=2,
                        page_type=PageType.CONCEPT,
                        heading="★ Matrix Diagonalization",
                        sections=[
                            ContentSection(
                                heading="★ Diagonalization Condition",
                                body="A square matrix A of order n is diagonalizable if and only if it has n linearly independent eigenvectors.",
                                formula="P^{-1} A P = D",
                                bullet_points=[
                                    "D is a diagonal matrix containing eigenvalues along its main diagonal",
                                    "P is the modal matrix whose columns are the corresponding eigenvectors",
                                    "D^k = P^{-1} A^k P  ==>  A^k = P D^k P^{-1}",
                                ],
                                callout_type="exam_tip",
                                callout_text="Key Exam Tip: If an n×n matrix has n distinct eigenvalues, it is ALWAYS diagonalizable!",
                            )
                        ],
                    ),
                ],
                key_takeaways=[
                    "Every square matrix satisfies its characteristic polynomial.",
                    "Cayley-Hamilton is the fastest way to compute matrix inverses and high powers.",
                    "A is diagonalizable iff geometric multiplicity = algebraic multiplicity for all eigenvalues.",
                ],
                exam_tip="In GATE/Semester exams: Pre-multiply A^n + ... + c_n I = 0 by A^-1 to instantly obtain A^-1 = -1/c_n (A^{n-1} + ... + c_1 I).",
                caption=(
                    "📐 Cayley-Hamilton Theorem & Matrix Diagonalization Made Easy!\n\n"
                    "One of the highest-yield topics in Linear Algebra for Engineering Mathematics and GATE.\n\n"
                    "Swipe for clear handwritten steps, inverse computation shortcut, and diagonalization conditions.\n\n"
                    "Save this post for your exam revision! 📌\n\n"
                    "#LinearAlgebra #EngineeringMathematics #BTech #GATE2026 #Mathematics #ExamPrep"
                ),
                hashtags=[
                    "#LinearAlgebra",
                    "#EngineeringMathematics",
                    "#BTech",
                    "#GATE2026",
                    "#Mathematics",
                    "#Calculus",
                    "#ExamPrep",
                    "#CollegeNotes",
                ],
            )

        # 3. GENERIC EDUCATIONAL TEMPLATE (for other topics like Python, OS, Networks)
        return NotePostContent(
            topic=topic,
            subject=category,
            difficulty=difficulty,
            title=topic,
            subtitle=f"Essential {category} Revision Notes",
            pages=[
                PageContent(
                    page_number=1,
                    page_type=PageType.CONCEPT,
                    heading=f"{topic} - Core Concepts",
                    sections=[
                        ContentSection(
                            heading=f"1. Overview of {topic}",
                            body=f"{topic} is a fundamental concept in {category} essential for system design and coding interviews.",
                            bullet_points=[
                                f"Core purpose and significance in modern {category} architectures",
                                "Improves modularity, efficiency, and resource utilization",
                                "Frequently tested in campus recruitment and technical interviews",
                            ],
                            callout_type="note",
                            callout_text=f"Remember: Master the basic trade-offs and edge cases of {topic}.",
                        ),
                        ContentSection(
                            heading="2. Implementation & Key Details",
                            body=f"Best practices and standard conventions when working with {topic}:",
                            bullet_points=[
                                "Keep time and space complexity optimal",
                                "Verify edge cases and boundary conditions",
                                "Adhere to standard conventions and clear naming",
                            ],
                            callout_type="exam_tip",
                            callout_text="Exam Tip: Always state time and space complexity explicitly.",
                        ),
                    ],
                )
            ],
            key_takeaways=[
                f"Understood core architecture of {topic}.",
                "Mastered trade-offs and practical application scenarios.",
            ],
            exam_tip=f"Always define {topic} with a clean diagram and example in exams.",
            caption=(
                f"📚 Master {topic} in under 60 seconds!\n\n"
                f"Essential revision notes on {topic} for {category} students.\n\n"
                "Save this post for your revisions! 🔖\n\n"
                f"#{category.replace(' ', '')} #ComputerScience #BTech #Engineering #StudyNotes"
            ),
            hashtags=[
                f"#{category.replace(' ', '')}",
                "#ComputerScience",
                "#BTech",
                "#Engineering",
                "#StudyNotes",
                "#PlacementPrep",
            ],
        )
