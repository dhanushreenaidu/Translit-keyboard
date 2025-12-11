# backend/src/services/tts_service.py

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Optional

import pyttsx3


class TTSService:
    def __init__(self, output_dir: Optional[str] = None) -> None:
        self.engine = pyttsx3.init()
        base = Path(output_dir) if output_dir is not None else Path("data/tts")
        base.mkdir(parents=True, exist_ok=True)
        self.output_dir = base

    def _select_voice(self, lang: str) -> None:
        """
        Try to pick a voice matching the lang code.
        On many systems there are no Indic voices installed,
        so this may just fall back to default English voice.
        """
        try:
            voices = self.engine.getProperty("voices")
            lang = lang.lower()
            for v in voices:
                name = (v.name or "").lower()
                vid = (v.id or "").lower()
                if lang == "hi" and ("hindi" in name or "hi-" in vid):
                    self.engine.setProperty("voice", v.id)
                    return
                if lang == "te" and ("telugu" in name or "te-" in vid):
                    self.engine.setProperty("voice", v.id)
                    return
            # else: keep default
        except Exception as e:
            print(f"[TTS] Voice selection error: {e}")

    def synthesize_to_file(self, text: str, lang: str) -> Path:
        text = text.strip()
        if not text:
            raise ValueError("Text is empty")

        self._select_voice(lang)

        out_path = self.output_dir / f"tts_{uuid.uuid4().hex}.wav"
        self.engine.save_to_file(text, str(out_path))
        self.engine.runAndWait()
        return out_path


tts_service = TTSService()
