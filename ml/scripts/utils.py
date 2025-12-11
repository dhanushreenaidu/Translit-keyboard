import json
import os


def build_char_vocab(pairs):
    chars = set()
    for p in pairs:
        chars.update(list(p["en"]))
        chars.update(list(p["native"]))

    char2idx = {"<pad>": 0, "<sos>": 1, "<eos>": 2}
    for c in sorted(chars):
        char2idx[c] = len(char2idx)

    idx2char = {i: c for c, i in char2idx.items()}
    return char2idx, idx2char


def encode_text(text, char2idx, max_len=40):
    seq = ["<sos>"] + list(text)[: max_len - 2] + ["<eos>"]
    ids = [char2idx.get(c, 0) for c in seq]
    return ids


def pad_seq(seq, max_len):
    if len(seq) < max_len:
        seq = seq + [0] * (max_len - len(seq))
    return seq[:max_len]
