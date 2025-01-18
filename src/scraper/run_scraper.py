"""CLI runner for scraping comments from Algerian YouTube content."""

import argparse
import json
import logging
import os
import sys
from typing import List

from src.scraper.youtube_scraper import YouTubeCommentScraper

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

DEFAULT_ALGERIAN_VIDEOS = [
    "https://www.youtube.com/watch?v=zsP8LMuiXyc",  # Algerian social podcast / interview
    "https://www.youtube.com/watch?v=BE_KNaRbFgQ",  # DZjoker comedy sketch
    "https://www.youtube.com/watch?v=vAEoUI3gDSE",  # Algerian street interview
    "https://www.youtube.com/watch?v=FoF-vO8yMWQ",  # Algerian discussion / culture
    "https://www.youtube.com/watch?v=o4MWN3tkLcw",  # Anas Tina Algerian satire / sketch
]


def run_scraper(
    urls: List[str],
    max_comments_per_video: int = 50,
    output_path: str = "data/raw/sample_raw_scraped.json",
) -> List[dict]:
    """Runs the YouTube comment scraper and saves raw results to JSON.

    Args:
        urls: List of YouTube video URLs to scrape.
        max_comments_per_video: Maximum comments to collect per video.
        output_path: Path where raw JSON data will be written.

    Returns:
        List of raw comment dictionaries.
    """
    scraper = YouTubeCommentScraper(max_comments_per_video=max_comments_per_video)
    logger.info(f"Starting scrape across {len(urls)} target videos...")
    raw_data = scraper.scrape_multiple_videos(urls)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(raw_data, f, ensure_ascii=False, indent=2)

    script_counts = {}
    for entry in raw_data:
        st = entry.get("script_type", "unknown")
        script_counts[st] = script_counts.get(st, 0) + 1

    logger.info(f"Done. Collected {len(raw_data)} total raw comments.")
    logger.info(f"Script breakdown: {script_counts}")
    logger.info(f"Raw data saved to: {output_path}")
    return raw_data


def main():
    parser = argparse.ArgumentParser(description="Scrape Algerian YouTube comments.")
    parser.add_argument(
        "--urls",
        nargs="+",
        default=DEFAULT_ALGERIAN_VIDEOS,
        help="List of YouTube URLs to scrape.",
    )
    parser.add_argument(
        "--max-comments",
        type=int,
        default=50,
        help="Max comments per video (default: 50).",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/raw/sample_raw_scraped.json",
        help="Output path for raw JSON data.",
    )
    args = parser.parse_args()
    run_scraper(
        urls=args.urls,
        max_comments_per_video=args.max_comments,
        output_path=args.output,
    )


if __name__ == "__main__":
    main()
