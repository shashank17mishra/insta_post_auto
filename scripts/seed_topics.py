"""Seed database with educational topics."""

import argparse
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings
from app.database.db import init_db
from app.database.repository import Repository
from app.logging_config import logger


def main():
    parser = argparse.ArgumentParser(description="Seed database with educational study topics.")
    parser.add_argument(
        "--file",
        type=str,
        default=str(settings.topics_file_path),
        help="Path to topics JSON file",
    )
    args = parser.parse_args()

    init_db()
    repo = Repository()
    topics_file = Path(args.file)

    if not topics_file.exists():
        logger.error(f"Topics file not found at: {topics_file}")
        sys.exit(1)

    count = repo.seed_topics_from_file(topics_file)
    print(f"Successfully seeded/updated {count} topics into database.")
    stats = repo.get_dashboard_stats()
    print(f"Database Stats: {stats}")


if __name__ == "__main__":
    main()
