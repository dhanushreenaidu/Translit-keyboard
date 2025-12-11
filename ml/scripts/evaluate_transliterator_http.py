# ml/scripts/evaluate_transliterator_http.py

"""
End-to-end evaluation of the transliteration API.

- Reads processed Aksharantar val files (JSONL)
- Calls FastAPI backend: POST /api/transliterate
- Computes:
    * exact string match accuracy
    * average character error rate (CER)

Prerequisites:
- Backend running at http://localhost:8000
- Val files exist at data/processed/aksharantar_<lang>_val.jsonl
"""

import json
from pathlib import Path
from typing import Tuple, List, Optional

import requests
from tqdm import tqdm


BACKEND_URL = "http://localhost:8000"
DATA_DIR = Path("data/processed")

# Adjust as you like
LANGUAGES = ["hi", "te", "ta"]
N_SAMPLES = 500


def extract_src_tgt(obj: dict, lang: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Try multiple possible key patterns to extract (src, tgt)
    so we don't depend on one fixed naming scheme.
    """

    # 1) Our preferred naming (what preprocess_aksharantar.py *should* use)
    src = obj.get("src")
    tgt = obj.get("tgt")
    if src and tgt:
        return str(src), str(tgt)

    # 2) Common alternates we might have used
    candidates_src = [
        "input",
        "en",
        "english",
        "roman",
        "english_word",
        "english word",
    ]
    candidates_tgt = [
        "output",
        "native",
        lang,  # e.g. "hi", "te", "ta"
        "native_word",
        "native word",
    ]

    for k in candidates_src:
        if k in obj and obj[k]:
            src = obj[k]
            break
    for k in candidates_tgt:
        if k in obj and obj[k]:
            tgt = obj[k]
            break

    if src and tgt:
        return str(src), str(tgt)

    return None, None


def load_pairs(lang: str, max_samples: int) -> List[Tuple[str, str]]:
    """
    Load (src, tgt) pairs from processed val file:
      data/processed/aksharantar_<lang>_val.jsonl
    """

    path = DATA_DIR / f"aksharantar_{lang}_val.jsonl"
    if not path.exists():
        raise FileNotFoundError(f"Val file not found: {path}")

    pairs: List[Tuple[str, str]] = []
    print(f"Reading: {path}")

    with path.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if max_samples is not None and i >= max_samples:
                break
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)

            src, tgt = extract_src_tgt(obj, lang)
            if src and tgt:
                pairs.append((src.strip(), tgt.strip()))

            # Debug: show first few examples / keys
            if i < 3:  # only first 3 lines
                print(f"[DEBUG {lang}] keys={list(obj.keys())} src={src} tgt={tgt}")

    return pairs


def levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if len(a) == 0:
        return len(b)
    if len(b) == 0:
        return len(a)

    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) + 1):
        dp[i][0] = i
    for j in range(len(b) + 1):
        dp[0][j] = j

    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,  # deletion
                dp[i][j - 1] + 1,  # insertion
                dp[i - 1][j - 1] + cost,  # substitution
            )
    return dp[-1][-1]


def evaluate_language(lang: str, max_samples: int) -> None:
    print(f"\n=== Evaluating language: {lang} ===")
    pairs = load_pairs(lang, max_samples)
    print(f"Loaded {len(pairs)} val samples (after filtering)")

    if not pairs:
        print("No samples found, skipping.")
        return

    exact_matches = 0
    total = 0
    total_cer = 0.0

    for src, tgt in tqdm(pairs, desc=f"[{lang}] Evaluating", unit="sample"):
        payload = {
            "text": src,
            "source_lang": "en",
            "target_lang": lang,
            "mode": "native",
        }

        try:
            resp = requests.post(
                f"{BACKEND_URL}/api/transliterate",
                json=payload,
                timeout=10,
            )
        except Exception as e:
            print(f"\nHTTP error for src='{src}': {e}")
            continue

        if resp.status_code != 200:
            print(f"\nHTTP {resp.status_code} for src='{src}': {resp.text}")
            continue

        data = resp.json()
        pred = data.get("primary", "").strip()
        if not pred:
            continue

        total += 1
        if pred == tgt:
            exact_matches += 1

        dist = levenshtein(pred, tgt)
        cer = dist / max(len(tgt), 1)
        total_cer += cer

    if total == 0:
        print("No successful predictions, cannot compute metrics.")
        return

    acc = exact_matches / total
    avg_cer = total_cer / total

    print(f"\nResults for {lang}:")
    print(f"  Samples evaluated : {total}")
    print(f"  Exact match acc   : {acc:.4f}")
    print(f"  Avg character CER : {avg_cer:.4f} (lower is better)")


def main() -> None:
    for lang in LANGUAGES:
        try:
            evaluate_language(lang, N_SAMPLES)
        except FileNotFoundError as e:
            print(e)


if __name__ == "__main__":
    main()
