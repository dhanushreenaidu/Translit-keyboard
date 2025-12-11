import json
import torch
from torch.utils.data import Dataset


class TransliterationDataset(Dataset):
    def __init__(self, jsonl_path: str, src_vocab, trg_vocab, max_len=40):
        self.samples = []
        self.src_vocab = src_vocab
        self.trg_vocab = trg_vocab
        self.max_len = max_len

        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                obj = json.loads(line)
                src = obj["src"]
                trg = obj["trg"]
                self.samples.append((src, trg))

    def encode_text(self, text, vocab):
        ids = [vocab["<sos>"]]
        for ch in text[: self.max_len - 2]:
            ids.append(vocab.get(ch, vocab["<unk>"]))
        ids.append(vocab["<eos>"])
        return ids

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        src, trg = self.samples[idx]
        src_ids = self.encode_text(src, self.src_vocab)
        trg_ids = self.encode_text(trg, self.trg_vocab)

        return torch.tensor(src_ids), torch.tensor(trg_ids)
