# Native Speaker Translation & Review Guidelines

This guide defines the translation and review workflow for creating parallel text pairs (Algerian Darija -> French / English).

---

## 1. Objectives
Scraped Darija text contains no pre-existing translations. To turn this raw corpus into training data for translation models (e.g. NLLB-200), native speakers must:
1. Validate that the text is authentic Algerian Darija (and flag any MSA or pure French that bypassed filtering).
2. Translate colloquial expressions accurately into French and English without over-standardizing or losing original tone.
3. Identify regional dialect markers (Algiers, Oran, Constantine, etc.) where obvious.

---

## 2. Handling Arabizi (Latin Script Darija)
Many entries are written in Arabizi (e.g. `yaatik saha khouya rak bzaf fort`).
- **Do not translate character-by-character**. Translate the actual colloquial meaning.
- **Numbers represent Arabic phonemes**:
  - `3` = ع (e.g., `m3ak` = معاك -> "with you")
  - `7` = ح (e.g., `saha` / `sa7a` = صحة -> "health / thanks")
  - `9` = ق (e.g., `9albi` = قلبي -> "my heart")
  - `5` = خ (e.g., `5ouya` = خويا -> "my brother")
  - `2` = ء (e.g., `ra2y` = رأي -> "opinion")

---

## 3. Translation Principles

### A. Tone and Register
- Maintain informal, colloquial tone where present (comments, jokes, street slang).
- Avoid artificially converting casual spoken phrasing into high-register literary language unless the speaker intended it.

### B. Cultural Idioms & Set Phrases
- `يعطيك الصحة` -> French: "Merci beaucoup" / "Chapeau", English: "Thank you / More power to you".
- `الله غالب` -> French: "C'est la vie / On n'y peut rien", English: "Nothing can be done / It is what it is".
- `كاين منها` -> French: "C'est vrai / Il y a du vrai là-dedans", English: "That's true / There's truth to that".
- `بزاف فور` -> French: "Vraiment excellent / Au top", English: "Really great / Top tier".

### C. Code-Switching & French Loanwords
- If an Algerian comment uses a French verb conjugated with Arabic grammar (e.g., `ybloqui` from *bloquer*, `ndemandi` from *demander*), translate the full sentence meaning directly.

---

## 4. Review & Quality Pass Columns (in `templates/crowdsourcing_batch.csv`)

| Column Name | Purpose | Accepted Values |
|:---|:---|:---|
| `id` | Unique sentence identifier | e.g. `dz_corpus_0001` |
| `cleaned_text` | Cleaned Darija text | Source text |
| `english_translation` | English parallel translation | Plain text |
| `french_translation` | French parallel translation | Plain text |
| `verified_algerian_darija` | Confirms whether text is authentic Darija | `Yes`, `No (MSA)`, `No (French)` |
| `regional_variant` | Regional dialect if recognizable | `Central (Algiers)`, `West (Oran)`, `East (Constantine)`, `South`, `General` |
| `reviewer_notes` | Optional notes on idioms, slang, or context | Free text |
