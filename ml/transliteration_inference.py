# backend/src/ml/transliteration_inference.py

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional, List

import torch
import torch.nn as nn

from ..config.settings import settings


class Encoder(nn.Module):
    def __init__(self, vocab_size: int, emb_dim: int, hid_dim: int):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, emb_dim)
        self.rnn = nn.LSTM(
            emb_dim,
            hid_dim,
            batch_first=True,
            bidirectional=True,
        )

    def forward(self, src: torch.Tensor):
        embedded = self.embedding(src)
        outputs, (hidden, cell) = self.rnn(embedded)
        hidden = hidden[0] + hidden[1]
        cell = cell[0] + cell[1]
        hidden = hidden.unsqueeze(0)
        cell = cell.unsqueeze(0)
        return outputs, hidden, cell


class Attention(nn.Module):
    def __init__(self, hid_dim: int):
        super().__init__()
        self.attn = nn.Linear(hid_dim * 3, hid_dim)
        self.v = nn.Linear(hid_dim, 1, bias=False)

    def forward(self, hidden: torch.Tensor, encoder_outputs: torch.Tensor):
        hidden = hidden[-1]
        batch_size = encoder_outputs.size(0)
        src_len = encoder_outputs.size(1)

        hidden_expanded = hidden.unsqueeze(1).repeat(1, src_len, 1)
        energy = torch.tanh(
            self.attn(torch.cat((hidden_expanded, encoder_outputs), dim=2))
        )
        attention = self.v(energy).squeeze(2)
        return torch.softmax(attention, dim=1)


class Decoder(nn.Module):
    def __init__(
        self, vocab_size: int, emb_dim: int, hid_dim: int, attention: Attention
    ):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, emb_dim)
        self.attention = attention
        self.rnn = nn.LSTM(hid_dim * 2 + emb_dim, hid_dim, batch_first=True)
        self.fc_out = nn.Linear(hid_dim * 3 + emb_dim, vocab_size)

    def forward(
        self,
        input: torch.Tensor,
        hidden: torch.Tensor,
        cell: torch.Tensor,
        encoder_outputs: torch.Tensor,
    ):
        input = input.unsqueeze(1)
        embedded = self.embedding(input)

        attn_weights = self.attention(hidden, encoder_outputs)
        attn_weights = attn_weights.unsqueeze(1)
        context = torch.bmm(attn_weights, encoder_outputs)

        rnn_input = torch.cat((embedded, context), dim=2)
        output, (hidden, cell) = self.rnn(rnn_input, (hidden, cell))

        output = output.squeeze(1)
        embedded = embedded.squeeze(1)
        context = context.squeeze(1)

        pred_input = torch.cat((output, context, embedded), dim=1)
        prediction = self.fc_out(pred_input)

        return prediction, hidden, cell


PAD_TOKEN = "<pad>"
SOS_TOKEN = "<sos>"
EOS_TOKEN = "<eos>"
UNK_TOKEN = "<unk>"


class Seq2Seq(nn.Module):
    def __init__(self, encoder: Encoder, decoder: Decoder, device: torch.device):
        super().__init__()
        self.encoder = encoder
        self.decoder = decoder
        self.device = device


class LoadedTranslitModel:
    def __init__(
        self,
        lang: str,
        model_path: Path,
        char2idx_path: Path,
        idx2char_path: Path,
        device: torch.device,
        emb_dim: int = 128,
        hid_dim: int = 256,
        max_len: int = 40,
    ):
        self.lang = lang
        self.device = device
        self.max_len = max_len

        with char2idx_path.open("r", encoding="utf-8") as f:
            self.char2idx: Dict[str, int] = json.load(f)

        with idx2char_path.open("r", encoding="utf-8") as f:
            raw_idx2char = json.load(f)
            self.idx2char: Dict[int, str] = {int(k): v for k, v in raw_idx2char.items()}

        self.pad_idx = self.char2idx.get(PAD_TOKEN, 0)
        self.sos_idx = self.char2idx.get(SOS_TOKEN, 1)
        self.eos_idx = self.char2idx.get(EOS_TOKEN, 2)
        self.unk_idx = self.char2idx.get(UNK_TOKEN, 3)

        vocab_size = len(self.char2idx)

        encoder = Encoder(vocab_size, emb_dim, hid_dim)
        attention = Attention(hid_dim)
        decoder = Decoder(vocab_size, emb_dim, hid_dim, attention)
        self.model = Seq2Seq(encoder, decoder, device).to(device)

        state = torch.load(model_path, map_location=device)
        self.model.load_state_dict(state)
        self.model.eval()

    def _encode_text(self, text: str) -> torch.Tensor:
        ids = [self.sos_idx]
        for ch in text:
            ids.append(self.char2idx.get(ch, self.unk_idx))
            if len(ids) >= self.max_len - 1:
                break
        ids.append(self.eos_idx)
        if len(ids) < self.max_len:
            ids += [self.pad_idx] * (self.max_len - len(ids))
        ids = ids[: self.max_len]
        return torch.tensor(ids, dtype=torch.long, device=self.device).unsqueeze(0)

    def _decode_ids(self, ids: List[int]) -> str:
        chars: List[str] = []
        for idx in ids:
            if idx in (self.pad_idx, self.sos_idx):
                continue
            if idx == self.eos_idx:
                break
            ch = self.idx2char.get(idx, "")
            if ch:
                chars.append(ch)
        return "".join(chars)

    def transliterate(self, text: str) -> str:
        with torch.no_grad():
            src = self._encode_text(text)
            encoder_outputs, hidden, cell = self.model.encoder(src)

            input_token = torch.tensor([self.sos_idx], device=self.device)
            decoded_ids: List[int] = []

            for _ in range(self.max_len):
                output, hidden, cell = self.model.decoder(
                    input_token, hidden, cell, encoder_outputs
                )
                next_id = int(output.argmax(dim=-1).item())
                if next_id == self.eos_idx:
                    break
                decoded_ids.append(next_id)
                input_token = torch.tensor([next_id], device=self.device)

        return self._decode_ids(decoded_ids)


class TransliterationEngine:
    def __init__(self, model_dir: Optional[str] = None):
        base = Path(model_dir) if model_dir is not None else Path(settings.MODEL_DIR)
        self.model_dir = base
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._cache: Dict[str, LoadedTranslitModel] = {}

    def _get_paths_for_lang(self, lang: str):
        model_path = self.model_dir / f"{lang}_model.pt"
        c2i_path = self.model_dir / f"{lang}_char2idx.json"
        i2c_path = self.model_dir / f"{lang}_idx2char.json"
        return model_path, c2i_path, i2c_path

    def _load_lang_model(self, lang: str) -> Optional[LoadedTranslitModel]:
        if lang in self._cache:
            return self._cache[lang]

        model_path, c2i_path, i2c_path = self._get_paths_for_lang(lang)
        if not (model_path.exists() and c2i_path.exists() and i2c_path.exists()):
            return None

        loaded = LoadedTranslitModel(
            lang=lang,
            model_path=model_path,
            char2idx_path=c2i_path,
            idx2char_path=i2c_path,
            device=self.device,
        )
        self._cache[lang] = loaded
        return loaded

    def transliterate(self, text: str, lang: str) -> Optional[str]:
        model = self._load_lang_model(lang)
        if model is None:
            return None
        return model.transliterate(text)


engine = TransliterationEngine()
