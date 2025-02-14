"""Text Cleaning and Deduplication Module for Darija Corpus."""

import re
from typing import Optional, Set

URL_REGEX = re.compile(r"https?://\S+|www\.\S+")
MENTION_REGEX = re.compile(r"@[\w\.\-]+")
MULTISPACE_REGEX = re.compile(r"\s+")
# Match emojis and special non-alphanumeric pictographs
EMOJI_REGEX = re.compile(
    r"[\U00010000-\U0010ffff]|[\u2000-\u3300]",
    flags=re.UNICODE,
)


def clean_text(raw_text: str) -> str:
    """Cleans raw text by stripping URLs, user tags, and normalizing spacing.

    Args:
        raw_text: Raw comment text.

    Returns:
        Cleaned text string.
    """
    if not raw_text or not isinstance(raw_text, str):
        return ""

    # Remove URLs and user tags
    cleaned = URL_REGEX.sub(" ", raw_text)
    cleaned = MENTION_REGEX.sub(" ", cleaned)

    # Normalize excessive newline and whitespace characters
    cleaned = cleaned.replace("\r", " ").replace("\n", " ")
    cleaned = MULTISPACE_REGEX.sub(" ", cleaned).strip()
    return cleaned


def count_words(text: str) -> int:
    """Counts the words in a string based on whitespace separation."""
    if not text:
        return 0
    return len(text.split())


class Deduplicator:
    """Maintains a cache of normalized texts to prevent duplicate entries."""

    def __init__(self):
        self.seen_signatures: Set[str] = set()

    def _get_signature(self, text: str) -> str:
        """Generates a normalized comparison signature."""
        # Lowercase, remove all non-alphanumeric characters, strip emojis
        normalized = text.lower()
        normalized = EMOJI_REGEX.sub("", normalized)
        normalized = re.sub(r"[^\w\s]", "", normalized)
        normalized = MULTISPACE_REGEX.sub("", normalized).strip()
        return normalized

    def is_duplicate(self, text: str) -> bool:
        """Checks whether the text is an exact or near-duplicate of previously seen text."""
        sig = self._get_signature(text)
        if not sig or sig in self.seen_signatures:
            return True
        self.seen_signatures.add(sig)
        return False
