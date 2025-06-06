"""Script Detection Module for Algerian Dialect Processing.

Classifies input text into:
- 'arabic': Text predominantly written in Arabic script.
- 'latin': Text predominantly written in Latin script (e.g., Arabizi or French).
- 'mixed': Code-switched or bilingual text containing both Arabic and Latin characters.
- 'unknown': Text containing no recognized alphabetic characters (e.g. symbols, emojis).
"""

import re
from typing import Literal

ScriptType = Literal["arabic", "latin", "mixed", "unknown"]

ARABIC_CHAR_PATTERN = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]")
LATIN_CHAR_PATTERN = re.compile(r"[a-zA-Z]")


def detect_script(text: str) -> ScriptType:
    """Detects the dominant script of a given string.

    Args:
        text: The raw text string.

    Returns:
        ScriptType: 'arabic', 'latin', 'mixed', or 'unknown'.
    """
    if not text or not isinstance(text, str):
        return "unknown"

    arabic_chars = len(ARABIC_CHAR_PATTERN.findall(text))
    latin_chars = len(LATIN_CHAR_PATTERN.findall(text))
    total_alpha = arabic_chars + latin_chars

    if total_alpha == 0:
        return "unknown"

    arabic_ratio = arabic_chars / total_alpha
    latin_ratio = latin_chars / total_alpha

    if arabic_ratio >= 0.75:
        return "arabic"
    elif latin_ratio >= 0.75:
        return "latin"
    else:
        return "mixed"
