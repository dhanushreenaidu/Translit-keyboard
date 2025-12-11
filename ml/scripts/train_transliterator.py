import os
import json
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm

from model import Encoder, Attention, Decoder, Seq2Seq

# -----------------------
# CONFIG
# -----------------------
LANG = "bn"  # train Hindi first
TRAIN_PATH = f"data/processed/aksharantar_{LANG}_train.jsonl"
VAL_PATH = f"data/processed/aksharantar_{LANG}_val.jsonl"

MAX_LEN = 40
BATCH_SIZE = 64
EPOCHS = 1
EMB_DIM = 128
HID_DIM = 256

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", DEVICE)

PAD_TOKEN = "<pad>"
SOS_TOKEN = "<sos>"
EOS_TOKEN = "<eos>"
UNK_TOKEN = "<unk>"


# -----------------------
# LOADING PAIRS
# -----------------------
def load_pairs(path, max_samples=None):
    """
    Load JSONL with {"en": "...", "native": "..."} pairs.
    """
    pairs = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            src = obj["en"]
            trg = obj["native"]
            pairs.append({"src": src, "trg": trg})
            if max_samples is not None and len(pairs) >= max_samples:
                break
    return pairs


# -----------------------
# VOCAB
# -----------------------
def build_char_vocab(pairs):
    """
    Build a shared char vocab over both src and trg chars.
    """
    chars = set()
    for p in pairs:
        chars.update(list(p["src"]))
        chars.update(list(p["trg"]))

    char2idx = {
        PAD_TOKEN: 0,
        SOS_TOKEN: 1,
        EOS_TOKEN: 2,
        UNK_TOKEN: 3,
    }
    for ch in sorted(chars):
        if ch not in char2idx:
            char2idx[ch] = len(char2idx)

    idx2char = {i: c for c, i in char2idx.items()}
    return char2idx, idx2char


def encode_text(text, char2idx, max_len=40):
    """
    Turn text into [<sos>, chars..., <eos>] ids, truncated to max_len.
    """
    ids = [char2idx[SOS_TOKEN]]
    for ch in text:
        ids.append(char2idx.get(ch, char2idx[UNK_TOKEN]))
        if len(ids) >= max_len - 1:
            break
    ids.append(char2idx[EOS_TOKEN])
    if len(ids) < max_len:
        ids += [char2idx[PAD_TOKEN]] * (max_len - len(ids))
    return ids[:max_len]


# -----------------------
# DATASET
# -----------------------
class TransliterationDataset(Dataset):
    def __init__(self, pairs, char2idx, max_len=40):
        self.pairs = pairs
        self.char2idx = char2idx
        self.max_len = max_len

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx):
        item = self.pairs[idx]
        src_ids = encode_text(item["src"], self.char2idx, self.max_len)
        trg_ids = encode_text(item["trg"], self.char2idx, self.max_len)
        return torch.tensor(src_ids, dtype=torch.long), torch.tensor(
            trg_ids, dtype=torch.long
        )


def collate_batch(batch):
    srcs, trgs = zip(*batch)
    srcs = torch.stack(srcs, dim=0)
    trgs = torch.stack(trgs, dim=0)
    return srcs, trgs


# -----------------------
# TRAINING
# -----------------------
def train():
    # 1) Load pairs
    print("Loading training pairs from:", TRAIN_PATH)
    train_pairs = load_pairs(TRAIN_PATH, max_samples=None)
    print("Loaded", len(train_pairs), "training pairs")

    print("Loading validation pairs from:", VAL_PATH)
    val_pairs = load_pairs(VAL_PATH, max_samples=20000)
    print("Loaded", len(val_pairs), "validation pairs")

    # 2) Vocab
    print("Building vocab from training pairs...")
    char2idx, idx2char = build_char_vocab(train_pairs)
    vocab_size = len(char2idx)
    pad_idx = char2idx[PAD_TOKEN]
    print("Vocab size:", vocab_size)

    os.makedirs("data/models", exist_ok=True)
    with open(f"data/models/{LANG}_char2idx.json", "w", encoding="utf-8") as f:
        json.dump(char2idx, f, ensure_ascii=False)
    with open(f"data/models/{LANG}_idx2char.json", "w", encoding="utf-8") as f:
        json.dump(idx2char, f, ensure_ascii=False)

    # 3) Datasets + loaders
    train_ds = TransliterationDataset(train_pairs, char2idx, MAX_LEN)
    val_ds = TransliterationDataset(val_pairs, char2idx, MAX_LEN)

    train_loader = DataLoader(
        train_ds,
        batch_size=BATCH_SIZE,
        shuffle=True,
        collate_fn=collate_batch,
    )
    val_loader = DataLoader(
        val_ds,
        batch_size=BATCH_SIZE,
        shuffle=False,
        collate_fn=collate_batch,
    )

    # 4) Model
    encoder = Encoder(vocab_size, EMB_DIM, HID_DIM)
    attention = Attention(HID_DIM)
    decoder = Decoder(vocab_size, EMB_DIM, HID_DIM, attention)
    model = Seq2Seq(encoder, decoder, DEVICE).to(DEVICE)

    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    criterion = nn.CrossEntropyLoss(ignore_index=pad_idx)

    # 5) Training loop
    for epoch in range(1, EPOCHS + 1):
        model.train()
        total_loss = 0.0

        print(f"\nEpoch {epoch}/{EPOCHS}")
        for src, trg in tqdm(train_loader):
            src = src.to(DEVICE)
            trg = trg.to(DEVICE)

            optimizer.zero_grad()
            outputs = model(src, trg)  # (batch, trg_len-1, vocab_size)

            # Flatten
            logits = outputs.reshape(-1, vocab_size)
            targets = trg[:, 1:].reshape(-1)  # shift target by 1 (skip <sos>)

            loss = criterion(logits, targets)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        avg_loss = total_loss / len(train_loader)
        print(f"Train loss: {avg_loss:.4f}")

    # 6) Save model
    save_path = f"data/models/{LANG}_model.pt"
    torch.save(model.state_dict(), save_path)
    print(f"\n✅ Saved model to: {save_path}")


if __name__ == "__main__":
    train()
