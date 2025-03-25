"""End-to-end processing pipeline for Algerian Darija dataset collection.

Orchestrates:
1. Raw ingestion
2. Cleaning & whitespace normalization
3. Length validation (>= 4 words)
4. Deduplication
5. Script detection (Arabic, Latin/Arabizi, Mixed)
6. Dialect filtering (excl. MSA and pure French)
7. Exporting to versioned JSON schema with 'needs_translation' flag
"""

import argparse
import json
import logging
import os
import sys
from typing import Any, Dict, List, Tuple

from src.filter.dialect_filter import filter_dialect
from src.filter.script_detector import detect_script
from src.filter.text_cleaner import Deduplicator, clean_text, count_words

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def process_corpus(
    raw_entries: List[Dict[str, Any]],
    min_word_count: int = 4,
) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    """Filters, cleans, and structures raw scraped comments into the curated corpus.

    Args:
        raw_entries: List of raw scraped comment objects.
        min_word_count: Minimum words required to retain an entry.

    Returns:
        (cleaned_dataset, statistics_dict)
    """
    deduplicator = Deduplicator()
    cleaned_dataset: List[Dict[str, Any]] = []
    stats = {
        "total_raw": len(raw_entries),
        "accepted_darija": 0,
        "filtered_too_short": 0,
        "filtered_duplicate": 0,
        "filtered_pure_msa": 0,
        "filtered_pure_french": 0,
        "filtered_insufficient_dialect": 0,
        "filtered_other": 0,
    }

    for idx, entry in enumerate(raw_entries, start=1):
        raw_text = entry.get("raw_text", "")
        cleaned = clean_text(raw_text)

        # Filter 1: Check length
        word_count = count_words(cleaned)
        if word_count < min_word_count:
            stats["filtered_too_short"] += 1
            continue

        # Filter 2: Deduplication
        if deduplicator.is_duplicate(cleaned):
            stats["filtered_duplicate"] += 1
            continue

        # Filter 3: Script detection
        script = detect_script(cleaned)
        if script == "unknown":
            stats["filtered_other"] += 1
            continue

        # Filter 4: Dialect validation (Darija vs MSA vs French)
        dialect_result = filter_dialect(cleaned, script)
        if not dialect_result["is_darija"]:
            status = dialect_result["status"]
            if status == "filtered_pure_msa":
                stats["filtered_pure_msa"] += 1
            elif status == "filtered_pure_french":
                stats["filtered_pure_french"] += 1
            else:
                stats["filtered_insufficient_dialect"] += 1
            continue

        # Validated authentic Algerian Darija entry
        item_id = f"dz_corpus_{len(cleaned_dataset) + 1:04d}"
        cleaned_entry = {
            "id": item_id,
            "source": entry.get("source", "youtube_comments"),
            "url_or_reference": entry.get("url_or_reference"),
            "video_title": entry.get("video_title", ""),
            "raw_text": raw_text,
            "cleaned_text": cleaned,
            "script_type": script,
            "word_count": word_count,
            "detected_dialect": "algerian_darija",
            "dialect_markers_found": dialect_result["markers"],
            "translation_status": "needs_translation",
            "target_translation": None,
        }
        cleaned_dataset.append(cleaned_entry)

    stats["accepted_darija"] = len(cleaned_dataset)
    return cleaned_dataset, stats


def run_pipeline(
    input_path: str = "data/raw/sample_raw_scraped.json",
    output_path: str = "data/cleaned/sample_cleaned_darija.json",
    min_word_count: int = 4,
) -> List[Dict[str, Any]]:
    """Runs the full cleaning pipeline and writes output JSON."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found at: {input_path}")

    with open(input_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    logger.info(f"Loaded {len(raw_data)} raw entries from {input_path}")
    cleaned_dataset, stats = process_corpus(raw_data, min_word_count=min_word_count)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cleaned_dataset, f, ensure_ascii=False, indent=2)

    logger.info("Pipeline Execution Summary:")
    for k, v in stats.items():
        logger.info(f"  {k}: {v}")
    logger.info(f"Cleaned dataset saved to: {output_path}")

    return cleaned_dataset


def main():
    parser = argparse.ArgumentParser(description="Process and filter raw Darija text into clean corpus.")
    parser.add_argument("--input", default="data/raw/sample_raw_scraped.json", help="Path to raw JSON.")
    parser.add_argument("--output", default="data/cleaned/sample_cleaned_darija.json", help="Path for cleaned JSON.")
    parser.add_argument("--min-words", type=int, default=4, help="Minimum words per entry (default: 4).")
    args = parser.parse_args()

    run_pipeline(input_path=args.input, output_path=args.output, min_word_count=args.min_words)


if __name__ == "__main__":
    from typing import Tuple
    main()
