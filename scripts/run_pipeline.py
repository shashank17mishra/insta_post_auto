"""Full automated end-to-end pipeline runner."""

import argparse
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings
from app.database.db import init_db
from app.database.models import PostStatus
from app.database.repository import Repository
from app.instagram.publisher import instagram_publisher
from app.services.generation_service import generation_service


def main():
    parser = argparse.ArgumentParser(description="Run complete automated generation and publication pipeline.")
    parser.add_argument("--topic", type=str, default=None, help="Optional topic name or ID (defaults to next pending)")
    parser.add_argument("--category", type=str, default=None, help="Filter by topic category")
    parser.add_argument("--auto-publish", action="store_true", help="Automatically approve and publish if generation succeeds")
    parser.add_argument("--mock", action="store_true", help="Force offline mock generation templates")

    args = parser.parse_args()

    init_db()
    repo = Repository()

    print("=======================================================")
    print("      STUDYNOTES AUTOPOSTER - AUTOMATION PIPELINE      ")
    print("=======================================================")

    # Step 1 & 2: Select & Generate
    post, errors = generation_service.generate_for_topic(
        topic_identifier=args.topic,
        category=args.category,
        force_mock=args.mock,
    )

    if errors or not post:
        print(f"\n[ERROR] Pipeline aborted: {errors}")
        sys.exit(1)

    print(f"\n[1/2] Note Generation Complete: Post #{post.id} ('{post.title}')")

    # Step 3: Optional Auto-Publish
    if args.auto_publish or settings.instagram_publish_enabled:
        print(f"\n[2/2] Auto-Publishing Post #{post.id} (DryRun={settings.dry_run})...")
        repo.update_post_status(post.id, PostStatus.APPROVED)
        success, msg = instagram_publisher.publish_post(post.id)
        if success:
            print(f"[SUCCESS] {msg}")
        else:
            print(f"[FAILED] {msg}")
            sys.exit(1)
    else:
        print(f"\n[2/2] Post #{post.id} saved as DRAFT in database.")
        print("To publish, review in dashboard or run: python -m scripts.publish_post --id " + str(post.id))

    print("\nPipeline run completed successfully.")


if __name__ == "__main__":
    main()
