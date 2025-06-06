# Project Roadmap: From Real Darija Corpus to Speech Recognition

This project collects, cleans, and translates real Algerian Darija text to train open-source translation (NLLB-200) and automatic speech recognition (Whisper / MMS) models.

---

## Phase 1: Data Collection & Corpus Foundation (Current)

### Step 1: Source Identification & Benchmarking
- Identify and rank scrapeable sources of authentic written Darija.
- Profile accessibility, anti-bot constraints, and dialect density (YouTube comments ranked #1, Reddit #2, forums #3).
- Document findings in `docs/sources_assessment.md`.

### Step 2: Scraping Engine
- Build standalone scraping scripts targeting public Algerian discussion content without requiring paid APIs.
- Extract raw text with metadata: source URL, channel, author, timestamp, script detection (`arabic`, `latin`, `mixed`).
- Output: `data/raw/sample_raw_scraped.json`.

### Step 3: Filtering & Cleaning
- Strip pure Modern Standard Arabic (MSA) using formal syntactic and lexical markers.
- Strip pure French comments using French stopword distribution and absence of Arabizi tokens.
- Exclude fragments shorter than 4 words.
- Remove exact and whitespace/emoji duplicates.
- Flag valid entries with `"translation_status": "needs_translation"`.
- Output: `data/cleaned/sample_cleaned_darija.json`.

### Step 4: Crowdsourced Translation Gap
- Set up a batch review spreadsheet (`templates/crowdsourcing_batch.csv`) for native speakers.
- Provide clear translation guidelines in `docs/translation_guide.md` covering Arabizi numerals (`3`, `7`, `9`, `5`, `2`) and cultural idioms.

### Step 5: Native Speaker Quality Pass
- Have Algerian native speakers review filtered sentences to flag any stray MSA or French that slipped through heuristics.
- Annotate regional varieties where applicable (e.g. Algiers, Oran, Constantine, Annaba).

### Step 6: Versioned Dataset Repository
- Maintain clean schema, CC-BY 4.0 licensing, and reproducible pipeline tooling.
- Release v0.1.0 seed corpus.

---

## Phase 2: Translation Modeling (NLLB-200)

### Step 7: Fine-Tuning NLLB-200
- Fine-tune Meta's NLLB-200 (600M / 1.3B) using authentic human-reviewed Darija pairs rather than synthetic machine-translated seed data.
- Train both directions: Darija <-> French and Darija <-> English.

### Step 8: Evaluation on Real Sentences
- Measure BLEU, chrF++, and human adequacy on a held-out test split of authentic sentences.
- Focus evaluation on code-switching (mixed French/Arabic) and Arabizi spelling variations.

### Step 9: Scale Data Scraping
- Expand the scraping pipeline across additional Algerian channels, podcasts, and community discussions.
- Run continuous filtering and batch translation rounds.

### Step 10: Retraining Iterations
- Retrain translation checkpoints in incremental batches (e.g., 5k, 20k, 50k sentence pairs) rather than waiting for one monolithic dataset.

---

## Phase 3: Public Release & Community Growth

### Step 11: Public Contribution Channels
- Open GitHub pull requests and an online submission form for community corrections and translations.

### Step 12: Hugging Face Dataset & Model Hub Release
- Upload dataset to Hugging Face Datasets (`algerian-darija-corpus`).
- Host fine-tuned translation models on Hugging Face Model Hub with an interactive demo Space.

---

## Phase 4: Speech-to-Text Phase (ASR)

### Step 13: Sourcing Paired Audio-Text Data
- Collect real Algerian audio from open podcasts, public interviews, and community recordings (not synthetic TTS).
- Align transcriptions and create timed audio segments.

### Step 14: Fine-Tuning Whisper / MMS
- Fine-tune OpenAI Whisper or Meta MMS on authentic Algerian speech.
- Benchmark word error rate (WER) across regional accents and publish open weights.
