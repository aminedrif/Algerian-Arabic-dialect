# Contributing to the Algerian Darija Corpus

Thank you for your interest in contributing to the authentic Algerian Arabic dialect dataset.

---

## Ways to Contribute

### 1. Provide Parallel Translations
- Review `templates/crowdsourcing_batch.csv`.
- Add French and English translations for unannotated sentences.
- Check `docs/translation_guide.md` for guidelines on Arabizi numerals (`3`, `7`, `9`, `5`, `2`) and cultural idioms.

### 2. Suggest New Authentic Sources
- If you know public Algerian YouTube channels, podcasts, or community forums with high Darija density, open an issue or submit a PR updating `docs/sources_assessment.md`.

### 3. Report Misclassified Entries
- If you notice Modern Standard Arabic (MSA) or pure French sentences that bypassed the filter, please report the entry ID in an issue.

---

## Pull Request Process
1. Fork or branch from `main`.
2. Make targeted additions or corrections.
3. Ensure existing tests pass:
   ```bash
   python -m pytest tests/test_filter.py
   ```
4. Open a Pull Request describing your changes.
