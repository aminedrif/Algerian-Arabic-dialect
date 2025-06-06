"""Evaluation script for NLLB-200 fine-tuned translation models."""

import argparse
import logging
import os
import sys
from typing import List

from src.training.dataset_loader import LANG_CODES, load_parallel_pairs

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def evaluate_model(args):
    """Evaluates translation performance on a held-out test dataset."""
    try:
        import torch
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
    except ImportError:
        logger.error(
            "Missing dependencies. Install them with: pip install -r requirements-train.txt"
        )
        sys.exit(1)

    src_lang_code = LANG_CODES["darija_arabic"]
    tgt_lang_code = LANG_CODES[args.target_lang]

    logger.info(f"Loading model and tokenizer from: {args.model_path}")
    tokenizer = AutoTokenizer.from_pretrained(
        args.model_path,
        src_lang=src_lang_code,
        tgt_lang=tgt_lang_code,
    )
    model = AutoModelForSeq2SeqLM.from_pretrained(args.model_path)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    model.eval()

    # Load test pairs
    test_pairs = load_parallel_pairs(args.test_file, target_lang=args.target_lang)
    if not test_pairs:
        logger.error(f"No translated evaluation pairs found in {args.test_file}")
        sys.exit(1)

    sources = [p["source"] for p in test_pairs]
    references = [p["target"] for p in test_pairs]

    logger.info(f"Translating {len(sources)} test sentences...")
    predictions = []

    # Get target language ID token for forced BOS token
    forced_bos_token_id = tokenizer.convert_tokens_to_ids(tgt_lang_code)

    for src in sources:
        inputs = tokenizer(
            src,
            return_tensors="pt",
            truncation=True,
            max_length=128,
        ).to(device)

        with torch.no_grad():
            generated_tokens = model.generate(
                **inputs,
                forced_bos_token_id=forced_bos_token_id,
                max_length=128,
                num_beams=4,
            )

        decoded = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
        predictions.append(decoded.strip())

    # Display comparison table
    print("\n" + "=" * 80)
    print("SAMPLE EVALUATION PREDICTIONS (Darija -> Target)")
    print("=" * 80)
    for i in range(min(5, len(sources))):
        print(f"\n[Sample {i + 1}]")
        print(f"Source (Darija): {sources[i]}")
        print(f"Prediction:      {predictions[i]}")
        print(f"Ground Truth:    {references[i]}")
    print("=" * 80 + "\n")

    # Compute BLEU / chrF if sacrebleu is available
    try:
        import sacrebleu
        bleu = sacrebleu.corpus_bleu(predictions, [[r] for r in references])
        chrf = sacrebleu.corpus_chrf(predictions, [[r] for r in references])
        logger.info(f"Corpus BLEU: {bleu.score:.2f}")
        logger.info(f"Corpus chrF++: {chrf.score:.2f}")
    except ImportError:
        logger.info("Install 'sacrebleu' to compute automated BLEU/chrF metrics: pip install sacrebleu")


def main():
    parser = argparse.ArgumentParser(description="Evaluate NLLB-200 translation model.")
    parser.add_argument(
        "--model_path",
        type=str,
        default="models/nllb-darija-v1/final_model",
        help="Path to fine-tuned model directory or base checkpoint.",
    )
    parser.add_argument(
        "--test_file",
        type=str,
        default="templates/crowdsourcing_batch.csv",
        help="Path to parallel test data (.csv or .json).",
    )
    parser.add_argument(
        "--target_lang",
        type=str,
        choices=["french", "english"],
        default="french",
        help="Target language.",
    )
    args = parser.parse_args()
    evaluate_model(args)


if __name__ == "__main__":
    main()
