import os
import json
import random
import argparse

RAW_DIR = "data/raw"
PRO_DIR = "data/processed"

# 9 Indic languages
LANGS = ["hi", "te", "ta", "kn", "ml", "mr", "bn", "gu", "pa"]


def load_tsv_pairs(tsv_path: str, max_samples=None):
    """
    Load (english, native) pairs from a TSV file.
    Each line: english<TAB>native
    """
    pairs = []

    if not os.path.exists(tsv_path):
        print(f"❌ File not found: {tsv_path}")
        return pairs

    with open(tsv_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = line.split("\t")
            if len(parts) != 2:
                continue

            en, native = parts
            en = en.strip()
            native = native.strip()

            if not en or not native:
                continue

            pairs.append({"en": en, "native": native})

            if max_samples is not None and len(pairs) >= max_samples:
                break

    return pairs


def save_jsonl(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


def preprocess_lang(lang, max_samples=None):
    """
    For one language:
      - Load raw TSV
      - Shuffle
      - Split into train / val / test (80/10/10)
      - Save as JSONL
    """
    tsv_path = os.path.join(RAW_DIR, f"aksharantar_{lang}.tsv")

    print(f"\n📂 Language: {lang}")
    print(f"   Reading from: {tsv_path}")

    pairs = load_tsv_pairs(tsv_path, max_samples=max_samples)
    if not pairs:
        print(f"   ⚠ No pairs loaded for {lang}, skipping.")
        return

    print(f"   Loaded {len(pairs)} pairs.")

    random.shuffle(pairs)
    n = len(pairs)

    n_train = int(0.8 * n)
    n_val = int(0.1 * n)
    n_test = n - n_train - n_val

    train = pairs[:n_train]
    val = pairs[n_train : n_train + n_val]
    test = pairs[n_train + n_val :]

    print(f"   Split: train={len(train)}, val={len(val)}, test={len(test)}")

    train_path = os.path.join(PRO_DIR, f"aksharantar_{lang}_train.jsonl")
    val_path = os.path.join(PRO_DIR, f"aksharantar_{lang}_val.jsonl")
    test_path = os.path.join(PRO_DIR, f"aksharantar_{lang}_test.jsonl")

    save_jsonl(train_path, train)
    save_jsonl(val_path, val)
    save_jsonl(test_path, test)

    print(f"   ✅ Saved {train_path}")
    print(f"   ✅ Saved {val_path}")
    print(f"   ✅ Saved {test_path}")


def main():
    parser = argparse.ArgumentParser(description="Preprocess Aksharantar TSV files")
    parser.add_argument(
        "--max-samples",
        type=int,
        default=None,
        help="Limit sample count per language (optional)",
    )
    args = parser.parse_args()

    if not os.path.exists(PRO_DIR):
        os.makedirs(PRO_DIR, exist_ok=True)

    print("🚀 Starting Aksharantar preprocessing...")

    for lang in LANGS:
        preprocess_lang(lang, max_samples=args.max_samples)

    print("\n🎉 Preprocessing complete!")


if __name__ == "__main__":
    main()
