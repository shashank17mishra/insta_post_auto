"""CLI tool to publish an approved note carousel to Instagram."""

import argparse
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings
from app.database.db import init_db
from app.database.repository import Repository
from app.instagram.publisher import instagram_publisher


def main():
    parser = argparse.ArgumentParser(description="Publish study note carousel to Instagram.")
    parser.add_argument("--id", type=int, default=None, help="Post ID to publish")
    parser.add_argument("--latest", action="store_true", help="Publish the most recently generated draft post")
    parser.add_argument("--force", action="store_true", help="Force publish even if status is not approved")
    parser.add_argument("--live", action="store_true", help="Disable dry-run mode for live posting")

    args = parser.parse_args()

    init_db()
    repo = Repository()

    post = None
    if args.id:
        post = repo.get_post(args.id)
    elif args.latest:
        drafts = repo.list_posts(status="draft", limit=1)
        if drafts:
            post = drafts[0]
        else:
            all_posts = repo.list_posts(limit=1)
            if all_posts:
                post = all_posts[0]

    if not post:
        print(f"Error: Post not found.")
        sys.exit(1)

    if args.live:
        settings.dry_run = False
        settings.instagram_publish_enabled = True
        instagram_publisher.client.dry_run = False

    print(f"Publishing Post #{post.id}: '{post.title}' (DryRun={instagram_publisher.client.dry_run})...")
    success, msg = instagram_publisher.publish_post(post.id, force=args.force)

    if success:
        print(f"\nSUCCESS: {msg}")
    else:
        print(f"\nFAILED: {msg}")
        sys.exit(1)


if __name__ == "__main__":
    main()
