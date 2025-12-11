# backend/src/services/language_service.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

from ..schemas.language import LanguageDetectRequest, LanguageDetectResponse


@dataclass
class ScriptRange:
    name: str
    lang_code: str
    start: int
    end: int


SCRIPT_RANGES = [
    ScriptRange("devanagari", "hi", 0x0900, 0x097F),
    ScriptRange("bengali", "bn", 0x0980, 0x09FF),
    ScriptRange("gurmukhi", "pa", 0x0A00, 0x0A7F),
    ScriptRange("gujarati", "gu", 0x0A80, 0x0AFF),
    ScriptRange("tamil", "ta", 0x0B80, 0x0BFF),
    ScriptRange("telugu", "te", 0x0C00, 0x0C7F),
    ScriptRange("kannada", "kn", 0x0C80, 0x0CFF),
    ScriptRange("malayalam", "ml", 0x0D00, 0x0D7F),
]


class LanguageService:
    def detect(self, req: LanguageDetectRequest) -> LanguageDetectResponse:
        text = (req.text or "").strip()
        if not text:
            return LanguageDetectResponse(
                text="",
                language="unknown",
                script="unknown",
                confidence=0.0,
            )

        latin_count = 0
        indic_counts: Dict[str, int] = {s.name: 0 for s in SCRIPT_RANGES}
        total_chars = 0

        for ch in text:
            if ch.isspace():
                continue
            total_chars += 1
            code = ord(ch)

            if ch.isascii():
                latin_count += 1
                continue

            for s in SCRIPT_RANGES:
                if s.start <= code <= s.end:
                    indic_counts[s.name] += 1
                    break

        if total_chars == 0:
            return LanguageDetectResponse(
                text=text,
                language="unknown",
                script="unknown",
                confidence=0.0,
            )

        best_script, best_count = self._max_script(indic_counts)

        # Only Latin → English
        if best_count == 0 and latin_count > 0:
            confidence = latin_count / total_chars
            return LanguageDetectResponse(
                text=text,
                language="en",
                script="latin",
                confidence=confidence,
            )

        # Only Indic script
        if best_count > 0 and latin_count == 0:
            lang_code = self._lang_for_script(best_script)
            confidence = best_count / total_chars
            return LanguageDetectResponse(
                text=text,
                language=lang_code,
                script=best_script,
                confidence=confidence,
            )

        # Mixed Latin + Indic
        if best_count > 0 and latin_count > 0:
            lang_code = self._lang_for_script(best_script)
            script = f"latin+{best_script}"
            confidence = best_count / (best_count + latin_count)
            return LanguageDetectResponse(
                text=text,
                language=lang_code if confidence >= 0.5 else "mixed",
                script=script,
                confidence=confidence,
            )

        return LanguageDetectResponse(
            text=text,
            language="unknown",
            script="unknown",
            confidence=0.0,
        )

    @staticmethod
    def _max_script(indic_counts: Dict[str, int]) -> Tuple[str, int]:
        best_script = "unknown"
        best_count = 0
        for script, count in indic_counts.items():
            if count > best_count:
                best_script = script
                best_count = count
        return best_script, best_count

    @staticmethod
    def _lang_for_script(script: str) -> str:
        for s in SCRIPT_RANGES:
            if s.name == script:
                return s.lang_code
        return "unknown"


language_service = LanguageService()
