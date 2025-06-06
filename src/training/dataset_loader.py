"""Dataset loader and tokenizer preprocessor for NLLB-200 fine-tuning."""

import csv
import json
import logging
import os
import random
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# NLLB-200 BCP-47 language codes
# ary_Arab is Moroccan Arabic in Arabic script, closest NLLB base for Algerian Darija
LANG_CODES = {
    "darija_arabic": "ary_Arab",
    "darija_arabizi": "ary_Arab",  # Can be mapped to ary_Arab or custom token
    "french": "fra_Latn",
    "english": "eng_Latn",
    "msa": "arb_Arab",
}


def load_parallel_pairs(
    file_path: str,
    target_lang: str = "french",
) -> List[Dict[str, str]]:
    """Loads parallel sentence pairs from JSON or CSV.

    Args:
        file_path: Path to dataset file (.json or .csv).
        target_lang: Target language ('french' or 'english').

    Returns:
        List of dicts: [{"source": ..., "target": ..., "script": ...}]
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    pairs = []
    target_col = f"{target_lang}_translation"

    if file_path.endswith(".json"):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data:
                src_text = item.get("cleaned_text") or item.get("raw_text")
                tgt_text = item.get(target_col) or item.get("target_translation")
                if src_text and tgt_text:
                    pairs.append({
                        "source": src_text.strip(),
                        "target": tgt_text.strip(),
                        "script": item.get("script_type", "arabic"),
                    })

    elif file_path.endswith(".csv"):
        with open(file_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                src_text = row.get("cleaned_text")
                tgt_text = row.get(target_col)
                if src_text and tgt_text:
                    pairs.append({
                        "source": src_text.strip(),
                        "target": tgt_text.strip(),
                        "script": row.get("script_type", "arabic"),
                    })

    logger.info(f"Loaded {len(pairs)} parallel pairs from {file_path}")
    return pairs


def create_train_val_test_splits(
    pairs: List[Dict[str, str]],
    train_ratio: float = 0.8,
    val_ratio: float = 0.1,
    seed: int = 42,
) -> Tuple[List[Dict[str, str]], List[Dict[str, str]], List[Dict[str, str]]]:
    """Splits pairs into reproducible train, validation, and test subsets."""
    random.seed(seed)
    shuffled = pairs.copy()
    random.shuffle(shuffled)

    n_total = len(shuffled)
    n_train = int(n_total * train_ratio)
    n_val = int(n_total * val_ratio)

    train_data = shuffled[:n_train]
    val_data = shuffled[n_train:n_train + n_val]
    test_data = shuffled[n_train + n_val:]

    logger.info(
        f"Dataset split ({n_total} total): "
        f"Train={len(train_data)}, Val={len(val_data)}, Test={len(test_data)}"
    )
    return train_data, val_data, test_data


def prepare_dataset_dict(
    train_pairs: List[Dict[str, str]],
    val_pairs: List[Dict[str, str]],
    test_pairs: List[Dict[str, str]],
):
    """Converts raw pairs into Hugging Face DatasetDict."""
    try:
        from datasets import Dataset, DatasetDict
    except ImportError:
        raise ImportError("Please install datasets: pip install datasets")

    return DatasetDict({
        "train": Dataset.from_list(train_pairs),
        "validation": Dataset.from_list(val_pairs),
        "test": Dataset.from_list(test_pairs),
    })
