"""Fine-tuning script for NLLB-200 on Algerian Darija translation pairs.

Supports translating:
- Algerian Darija -> French (ary_Arab -> fra_Latn)
- Algerian Darija -> English (ary_Arab -> eng_Latn)
"""

import argparse
import logging
import os
import sys

from src.training.dataset_loader import (
    LANG_CODES,
    create_train_val_test_splits,
    load_parallel_pairs,
    prepare_dataset_dict,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def train(args):
    """Executes the NLLB-200 fine-tuning workflow."""
    try:
        import torch
        from transformers import (
            AutoModelForSeq2SeqLM,
            AutoTokenizer,
            DataCollatorForSeq2Seq,
            Seq2SeqTrainer,
            Seq2SeqTrainingArguments,
        )
    except ImportError:
        logger.error(
            "Missing machine learning dependencies. "
            "Install training requirements with: pip install -r requirements-train.txt"
        )
        sys.exit(1)

    # 1. Load data
    logger.info(f"Loading parallel pairs from {args.data_file}...")
    pairs = load_parallel_pairs(args.data_file, target_lang=args.target_lang)
    if len(pairs) == 0:
        logger.error(
            "No parallel translation pairs found in the dataset file. "
            "Please ensure human translations are added to the CSV or JSON before training."
        )
        sys.exit(1)

    train_data, val_data, test_data = create_train_val_test_splits(
        pairs,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
    )
    dataset_dict = prepare_dataset_dict(train_data, val_data, test_data)

    # 2. Setup tokenizer and language tags
    src_lang_code = LANG_CODES["darija_arabic"]
    tgt_lang_code = LANG_CODES[args.target_lang]

    logger.info(f"Loading tokenizer and model: {args.model_name}")
    logger.info(f"Translation direction: {src_lang_code} -> {tgt_lang_code}")

    tokenizer = AutoTokenizer.from_pretrained(
        args.model_name,
        src_lang=src_lang_code,
        tgt_lang=tgt_lang_code,
    )

    model = AutoModelForSeq2SeqLM.from_pretrained(args.model_name)

    # 3. Tokenize dataset
    def preprocess_function(examples):
        inputs = examples["source"]
        targets = examples["target"]
        model_inputs = tokenizer(
            inputs,
            max_length=args.max_source_length,
            truncation=True,
            padding="max_length" if args.pad_to_max_length else False,
        )
        labels = tokenizer(
            text_target=targets,
            max_length=args.max_target_length,
            truncation=True,
            padding="max_length" if args.pad_to_max_length else False,
        )
        model_inputs["labels"] = labels["input_ids"]
        return model_inputs

    logger.info("Tokenizing datasets...")
    tokenized_datasets = dataset_dict.map(
        preprocess_function,
        batched=True,
        remove_columns=dataset_dict["train"].column_names,
    )

    # 4. Training Arguments
    training_args = Seq2SeqTrainingArguments(
        output_dir=args.output_dir,
        eval_strategy="epoch",
        save_strategy="epoch",
        learning_rate=args.learning_rate,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        weight_decay=0.01,
        save_total_limit=2,
        num_train_epochs=args.epochs,
        predict_with_generate=True,
        fp16=torch.cuda.is_available() and args.fp16,
        logging_dir=os.path.join(args.output_dir, "logs"),
        logging_steps=10,
        load_best_model_at_end=True,
        report_to="none",
    )

    data_collator = DataCollatorForSeq2Seq(
        tokenizer,
        model=model,
        padding="longest",
    )

    # 5. Trainer
    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["validation"],
        tokenizer=tokenizer,
        data_collator=data_collator,
    )

    logger.info("Starting training...")
    trainer.train()

    # 6. Save best model & tokenizer
    final_model_path = os.path.join(args.output_dir, "final_model")
    logger.info(f"Saving final fine-tuned model to {final_model_path}")
    trainer.save_model(final_model_path)
    tokenizer.save_pretrained(final_model_path)
    logger.info("Training complete.")


def main():
    parser = argparse.ArgumentParser(description="Fine-tune NLLB-200 on Algerian Darija.")
    parser.add_argument(
        "--model_name",
        type=str,
        default="facebook/nllb-200-distilled-600M",
        help="HuggingFace model checkpoint.",
    )
    parser.add_argument(
        "--data_file",
        type=str,
        default="templates/crowdsourcing_batch.csv",
        help="Path to translated dataset (.csv or .json).",
    )
    parser.add_argument(
        "--target_lang",
        type=str,
        choices=["french", "english"],
        default="french",
        help="Target language for translation.",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="models/nllb-darija-v1",
        help="Output directory for model checkpoints.",
    )
    parser.add_argument("--epochs", type=int, default=5, help="Number of training epochs.")
    parser.add_argument("--batch_size", type=int, default=8, help="Batch size per device.")
    parser.add_argument("--learning_rate", type=float, default=5e-5, help="Learning rate.")
    parser.add_argument("--max_source_length", type=int, default=128, help="Max source tokens.")
    parser.add_argument("--max_target_length", type=int, default=128, help="Max target tokens.")
    parser.add_argument("--train_ratio", type=float, default=0.8, help="Train split fraction.")
    parser.add_argument("--val_ratio", type=float, default=0.1, help="Val split fraction.")
    parser.add_argument("--fp16", action="store_true", help="Enable FP16 mixed precision.")
    parser.add_argument("--pad_to_max_length", action="store_true", help="Pad all samples.")
    args = parser.parse_args()

    train(args)


if __name__ == "__main__":
    main()
