# backend/src/services/transliteration_service.py

from __future__ import annotations

from typing import List, Tuple, Any

from ..ml.transliteration_inference import engine
from ..schemas.transliteration import (
    TransliterationRequest,
    TransliterationResponse,
    TransliterationCandidate,
)

# Simple list of English words / proper nouns we usually want to keep as-is
ENGLISH_KEEP = {
    "hyderabad",
    "bangalore",
    "mumbai",
    "delhi",
    "college",
    "school",
    "office",
    "instagram",
    "facebook",
    "whatsapp",
    "java",
    "python",
    "c++",
    "btech",
    "mtech",
    "email",
}


def should_keep_english(token: str) -> bool:
    """
    Heuristic for MIX mode:
    Return True if this token should STAY in English (not transliterated).
    """
    if not token:
        return False

    low = token.lower()

    if low in ENGLISH_KEEP:
        return True

    if any(ch.isdigit() for ch in token):
        return True
    if any(ch in "@#&/._-" for ch in token):
        return True

    if token[0].isupper():
        return True

    return False


class TransliterationService:
    """
    High-level service that:
    - Splits sentences into tokens
    - In MIX mode: keeps some English tokens as-is
    - Calls the low-level ML engine word-by-word for others
    - Re-joins with spaces so output keeps word boundaries
    """

    def _transliterate_word(self, word: str, target_lang: str) -> Tuple[str, str]:
        """
        Call the ML engine for a single word.
        Returns (primary_output, provider_used)
        """
        if not word.strip():
            return "", "none"

        try:
            result: Any = engine.transliterate(word, lang=target_lang)
        except Exception as e:
            print(f"[TranslitService] Engine error for '{word}': {e}")
            return word, "stub"

        if result is None:
            return word, "stub"

        if isinstance(result, str):
            return result, "ml-local"

        if isinstance(result, dict):
            primary = result.get("primary") or result.get("text") or word
            provider = result.get("provider", "ml-local")
            return primary, provider

        return str(result), "ml-local"

    def transliterate(self, req: TransliterationRequest) -> TransliterationResponse:
        text = (req.text or "").strip()

        if not text:
            return TransliterationResponse(
                input_text="",
                primary="",
                candidates=[],
                source_lang=req.source_lang,
                target_lang=req.target_lang,
                mode=req.mode,
                provider="none",
            )

        tokens = text.split()

        out_tokens: List[str] = []
        provider_overall = "ml-local-word"

        for tok in tokens:
            if req.mode == "mix" and should_keep_english(tok):
                out_tokens.append(tok)
                continue

            word_out, provider = self._transliterate_word(tok, req.target_lang)
            out_tokens.append(word_out)
            if provider == "stub":
                provider_overall = "stub"

        primary_phrase = " ".join(out_tokens)

        candidates = [
            TransliterationCandidate(text=primary_phrase, score=1.0),
        ]

        return TransliterationResponse(
            input_text=text,
            primary=primary_phrase,
            candidates=candidates,
            source_lang=req.source_lang,
            target_lang=req.target_lang,
            mode=req.mode,
            provider=provider_overall,
        )


transliteration_service = TransliterationService()
