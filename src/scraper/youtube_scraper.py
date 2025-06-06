"""YouTube Comment Scraper for Algerian Content using yt-dlp.

Extracts authentic user comments without requiring Google API credentials.
Identifies script type and attaches full source provenance.
"""

import logging
from typing import Any, Dict, List, Optional
import yt_dlp

from src.filter.script_detector import detect_script

logger = logging.getLogger(__name__)


class YouTubeCommentScraper:
    """Extracts comments from public YouTube videos using yt-dlp."""

    def __init__(self, max_comments_per_video: int = 50):
        """Initializes the scraper.

        Args:
            max_comments_per_video: Max number of comments to extract per video.
        """
        self.max_comments_per_video = max_comments_per_video
        self.ydl_opts = {
            "getcomments": True,
            "extract_flat": False,
            "skip_download": True,
            "extractor_args": {
                "youtube": {
                    "max_comments": [str(max_comments_per_video), "all", str(max_comments_per_video), "0"]
                }
            },
            "quiet": True,
            "no_warnings": True,
        }

    def scrape_video(self, video_url: str) -> List[Dict[str, Any]]:
        """Scrapes comments from a single YouTube video URL.

        Args:
            video_url: Public YouTube video link.

        Returns:
            List of raw comment dictionaries with source attribution and script detection.
        """
        logger.info(f"Extracting comments from: {video_url}")
        comments_data: List[Dict[str, Any]] = []

        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                raw_comments = info.get("comments") or []
                video_title = info.get("title", "")
                channel = info.get("uploader", "")

                for c in raw_comments:
                    text = c.get("text")
                    if not text:
                        continue

                    script = detect_script(text)
                    if script == "unknown":
                        continue

                    comments_data.append({
                        "source": "youtube_comments",
                        "url_or_reference": video_url,
                        "comment_id": c.get("id"),
                        "author": c.get("author"),
                        "video_title": video_title,
                        "channel": channel,
                        "raw_text": text,
                        "script_type": script,
                        "like_count": c.get("like_count", 0),
                        "timestamp": c.get("timestamp"),
                    })

            logger.info(f"Successfully scraped {len(comments_data)} comments from {video_url}")
        except Exception as e:
            logger.error(f"Failed to scrape comments from {video_url}: {e}")

        return comments_data

    def scrape_multiple_videos(self, video_urls: List[str]) -> List[Dict[str, Any]]:
        """Scrapes comments across multiple Algerian YouTube videos.

        Args:
            video_urls: List of YouTube video URLs.

        Returns:
            Aggregated list of scraped comment dictionaries.
        """
        all_comments: List[Dict[str, Any]] = []
        for url in video_urls:
            all_comments.extend(self.scrape_video(url))
        return all_comments
