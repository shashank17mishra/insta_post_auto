"""CLI tool to generate study notes for a topic."""

import argparse
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings
from app.database.db import init_db
from app.database.repository import Repository
from app.services.generation_service import generation_service


def main():
    parser = argparse.ArgumentParser(description="Generate educational study note Instagram carousel.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--topic", type=str, help="Specific topic name or ID to generate")
    group.add_argument("--next", action="store_true", help="Generate the next priority pending topic")

    parser.add_argument("--category", type=str, default=None, help="Filter by subject category")
    parser.add_argument("--mock", action="store_true", help="Force use of curated offline mock templates")

    args = parser.parse_args()

    init_db()
    topic_target = args.topic if not args.next else None

    print(f"Generating notes for: {topic_target or 'NEXT pending topic'}...")
    post, errors = generation_service.generate_for_topic(
        topic_identifier=topic_target,
        category=args.category,
        force_mock=args.mock,
    )

    if errors or not post:
        print(f"FAILED: {errors}")
        sys.exit(1)

    repo = Repository()
    pages = repo.get_pages_for_post(post.id)
    print("\n=======================================================")
    print(f"SUCCESSFULLY GENERATED POST #{post.id}")
    print("=======================================================")
    print(f"Title: {post.title}")
    print(f"Topic ID: {post.topic_id}")
    print(f"Status: {post.status.value}")
    print(f"Rendered Slides: {len(pages)}")
    for p in pages:
        print(f"  - Slide {p.page_number}: {p.file_path}")
    print(f"Draft directory: {settings.output_dir / 'drafts' / str(post.id)}")
    print("=======================================================\n")


if __name__ == "__main__":
    main()
