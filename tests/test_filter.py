"""Unit tests for script detection, dialect validation, and text cleaning."""

import pytest
from src.filter.script_detector import detect_script
from src.filter.dialect_filter import filter_dialect
from src.filter.text_cleaner import clean_text, count_words, Deduplicator


def test_script_detection():
    # Arabic script test
    assert detect_script("واش راك خويا لاباس عليك") == "arabic"
    # Latin Arabizi test
    assert detect_script("khouya rak mlih bzaf") == "latin"
    # Mixed script test
    assert detect_script("يعطيك الصحة خويا c'est magnifique") == "mixed"
    # Symbols only
    assert detect_script("😂😂🔥 12345 !!!") == "unknown"


def test_arabic_darija_validation():
    # Authentic Darija with negative circumfix and demonstratives
    darija_sample = "ماكانش منها واش راك تهدر يا خويا كاين بزاف حوايج ملاح"
    res = filter_dialect(darija_sample, "arabic")
    assert res["is_darija"] is True
    assert res["status"] == "algerian_darija"
    assert "ماكانش" in res["markers"] or "واش" in res["markers"]

    # Pure Modern Standard Arabic (MSA) - should be excluded
    msa_sample = "سوف تقوم الحكومة بمناقشة هذا المشروع حيث تم الإعلان عن ذلك رسميا"
    res_msa = filter_dialect(msa_sample, "arabic")
    assert res_msa["is_darija"] is False
    assert res_msa["status"] == "filtered_pure_msa"


def test_arabizi_vs_french_validation():
    # Authentic Arabizi with numerals (3 = ع, 7 = ح) and vocabulary
    arabizi_sample = "yaatik saha sahbi rak fort bzaf m3ak daymen"
    res_arabizi = filter_dialect(arabizi_sample, "latin")
    assert res_arabizi["is_darija"] is True
    assert res_arabizi["status"] == "algerian_darija_arabizi"

    # Pure French comment without Darija tokens - should be excluded
    french_sample = "C'est une très bonne initiative merci beaucoup pour cette vidéo instructive et bon courage pour la suite"
    res_french = filter_dialect(french_sample, "latin")
    assert res_french["is_darija"] is False
    assert res_french["status"] == "filtered_pure_french"


def test_cleaner_and_word_count():
    raw = "  @user123  Check this out: https://youtube.com/watch?v=xyz  راك مليح خويا  "
    cleaned = clean_text(raw)
    assert "@user123" not in cleaned
    assert "https://" not in cleaned
    assert "راك مليح خويا" in cleaned
    assert count_words(cleaned) == 6

    # Test under 4 words
    assert count_words("راك مليح خويا") == 3


def test_deduplicator():
    dedup = Deduplicator()
    text = "راك فاهم خويا العزيز"
    assert dedup.is_duplicate(text) is False
    # Exact duplicate
    assert dedup.is_duplicate(text) is True
    # Duplicate with minor spacing and emoji variations
    assert dedup.is_duplicate("  راك فاهم خويا العزيز  🔥  ") is True
