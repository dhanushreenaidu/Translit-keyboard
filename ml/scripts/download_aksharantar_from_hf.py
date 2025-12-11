import os
import json
import zipfile
from typing import Dict

from huggingface_hub import hf_hub_download

REPO_ID = "ai4bharat/Aksharantar"
RAW_DIR = "data/raw"

# Our 9 languages (2-letter codes) -> 3-letter codes used by Aksharantar
LANG_MAP_2_TO_3: Dict[str, str] = {
    "hi": "hin",  # Hindi
    "te": "tel",  # Telugu
    "ta": "tam",  # Tamil
    "kn": "kan",  # Kannada
    "ml": "mal",  # Malayalam
    "mr": "mar",  # Marathi
    "bn": "ben",  # Bengali
    "gu": "guj",  # Gujarati
    "pa": "pan",  # Punjabi
}


def download_zip(lang3: str) -> str:
    """
    Download <lang3>.zip (e.g. 'hin.zip') from HuggingFace to local cache
    and return the local file path.
    """
    filename = f"{lang3}.zip"
    print(f"⏬ Downloading {filename} from HuggingFace...")
    local_path = hf_hub_download(
        repo_id=REPO_ID,
        filename=filename,
        repo_type="dataset",
    )
    print(f"   -> Cached at: {local_path}")
    return local_path


def extract_train_to_tsv(lang_short: str, lang3: str, zip_path: str) -> None:
    """
    From <lang3>.zip, read *_train.json and write a TSV:
    data/raw/aksharantar_<lang_short>.tsv
    with columns: english<TAB>native
    """
    os.makedirs(RAW_DIR, exist_ok=True)
    out_tsv = os.path.join(RAW_DIR, f"aksharantar_{lang_short}.tsv")

    print(f"📦 Processing {zip_path} -> {out_tsv}")

    with zipfile.ZipFile(zip_path, "r") as zf:
        # Find the train JSON file (e.g. 'hin_train.json')
        train_json_name = None
        for name in zf.namelist():
            if name.endswith("_train.json"):
                train_json_name = name
                break

        if train_json_name is None:
            print(f"❌ No *_train.json found inside {zip_path}")
            return

        print(f"   Using train file inside zip: {train_json_name}")

        with zf.open(train_json_name) as f:
            # Read full content as text
            raw_bytes = f.read()
            text = raw_bytes.decode("utf-8")

        # Try: whole file is a JSON list
        records = None
        try:
            obj = json.loads(text)
            if isinstance(obj, list):
                records = obj
            elif isinstance(obj, dict):
                # Just in case, single object
                records = [obj]
        except json.JSONDecodeError:
            # Fallback: assume JSON Lines (one object per line)
            records = []
            for line in text.splitlines():
                line = line.strip()
                if not line:
                    continue
                records.append(json.loads(line))

    # Write TSV: english word \t native word
    num_written = 0
    with open(out_tsv, "w", encoding="utf-8") as out_f:
        for row in records:
            # According to dataset card, keys are:
            # 'native word', 'english word', plus 'unique_identifier','source','score' etc.
            native = str(row.get("native word", "")).strip()
            english = str(row.get("english word", "")).strip()

            if not native or not english:
                continue

            out_f.write(f"{english}\t{native}\n")
            num_written += 1

    print(f"✅ Wrote {num_written} pairs to {out_tsv}")


def main():
    os.makedirs(RAW_DIR, exist_ok=True)

    for short, lang3 in LANG_MAP_2_TO_3.items():
        try:
            zip_path = download_zip(lang3)
            extract_train_to_tsv(short, lang3, zip_path)
        except Exception as e:
            print(f"❌ Error for {short} ({lang3}): {e}")

    print("🎉 All requested languages processed.")


if __name__ == "__main__":
    main()
