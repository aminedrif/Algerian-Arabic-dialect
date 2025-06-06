# Algerian Darija (Algerian Arabic Dialect) Corpus & Toolkit

An open-source data collection, filtering, and annotation pipeline built to create an authentic (non-synthetic) dataset of Algerian Darija text. This dataset forms the foundation for machine translation (NLLB-200) and speech-to-text models (Whisper / MMS).

---

## Why Authentic Data?
Synthetic text generation often fails for Algerian Darija because it lacks:
- **Natural Code-Switching**: Spontaneous blending of Algerian Arabic syntax with French and Tamazight loanwords.
- **Arabizi Phonetics**: Colloquial Latin script usage with digit representations for Arabic phonemes (`3` = ع, `7` = ح, `9` = ق, `5` = خ, `2` = ء).
- **Everyday Idioms**: Contextual phrases (`يعطيك الصحة`, `ماكانش منها`, `بزاف فور`, `الله غالب`) that language models tend to over-correct into Modern Standard Arabic.

Every entry in this corpus originates from real public discussions authored by Algerian speakers.

---

## Repository Structure

```
Algerian-Arabic-dialect/
├── data/
│   ├── raw/
│   │   └── sample_raw_scraped.json          # Raw comments with platform provenance
│   └── cleaned/
│       └── sample_cleaned_darija.json       # Validated, filtered Algerian Darija entries
├── docs/
│   ├── sources_assessment.md                # Evaluation of scrapeable Algerian sources
│   ├── translation_guide.md                 # Guidelines for native translators & reviewers
│   └── roadmap.md                           # 14-step project roadmap (text corpus to speech)
├── src/
│   ├── __init__.py
│   ├── pipeline.py                          # Full end-to-end ingestion & cleaning pipeline
│   ├── filter/
│   │   ├── __init__.py
│   │   ├── dialect_filter.py                # Darija vs MSA/French classification
│   │   ├── script_detector.py               # Arabic vs Latin vs Mixed script detection
│   │   └── text_cleaner.py                  # Deduplication, noise cleaning & length check
│   └── scraper/
│       ├── __init__.py
│       ├── run_scraper.py                   # Scraper CLI runner
│       └── youtube_scraper.py               # yt-dlp backend for public comment extraction
├── templates/
│   └── crowdsourcing_batch.csv              # Spreadsheet template for translation passes
├── tests/
│   ├── __init__.py
│   └── test_filter.py                       # Unit tests for dialect validation & cleaning
├── requirements.txt                         # Project dependencies
├── LICENSE                                  # CC-BY 4.0 (Data) / MIT (Code)
└── README.md
```

---

## Quick Start

### 1. Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/aminedrif/Algerian-Arabic-dialect.git
cd Algerian-Arabic-dialect
pip install -r requirements.txt
```

### 2. Run Tests
```bash
python -m pytest tests/test_filter.py
```

### 3. Run Scraper
Scrape comments from authentic Algerian YouTube videos (podcasts, comedy sketches, street interviews):
```bash
python -m src.scraper.run_scraper --max-comments 50 --output data/raw/sample_raw_scraped.json
```

### 4. Run Cleaning & Filtering Pipeline
Filter out pure MSA, pure French, short fragments (< 4 words), and duplicates:
```bash
python -m src.pipeline --input data/raw/sample_raw_scraped.json --output data/cleaned/sample_cleaned_darija.json
```

---

## Dataset Schema

Each entry in `data/cleaned/sample_cleaned_darija.json` follows this schema:

```json
{
  "id": "dz_corpus_0001",
  "source": "youtube_comments",
  "url_or_reference": "https://www.youtube.com/watch?v=zsP8LMuiXyc",
  "video_title": "Algerian social podcast",
  "raw_text": "لا معندهاش دخل انت فقط ماكش متعلم وماكش مثقف...",
  "cleaned_text": "لا معندهاش دخل انت فقط ماكش متعلم وماكش مثقف...",
  "script_type": "arabic",
  "word_count": 142,
  "detected_dialect": "algerian_darija",
  "dialect_markers_found": [
    "معندهاش",
    "ماكش",
    "بصح",
    "كي",
    "جيت",
    "راك",
    "حاب",
    "نتاع",
    "منيش",
    "بلاك",
    "شوي"
  ],
  "translation_status": "needs_translation",
  "target_translation": null
}
```

---

## Current Sample Statistics
- **Raw comments scraped**: 282 entries
- **Cleaned authentic Darija entries**: 68 entries
  - Arabic script: ~60%
  - Arabizi (Latin script): ~40%
- **Rejections**:
  - Excluded pure French: 73 comments
  - Excluded pure MSA: 5 comments
  - Excluded short fragments (< 4 words): 53 comments
  - Excluded duplicates: 1 comment

---

## Contributing to Translations
Scraped Darija arrives without translations. To contribute manual French or English translations:
1. Open `templates/crowdsourcing_batch.csv` in Excel or Google Sheets.
2. Read the guidelines in `docs/translation_guide.md`.
3. Submit completed batches via Pull Request or community channels.

---

## License
- **Dataset**: [Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE)
- **Source Code**: [MIT License](LICENSE)
