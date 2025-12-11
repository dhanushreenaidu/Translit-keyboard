# backend/src/utils/script_detect.py


def is_telugu(text: str) -> bool:
    return any(0x0C00 <= ord(ch) <= 0x0C7F for ch in text)


def is_hindi(text: str) -> bool:
    return any(0x0900 <= ord(ch) <= 0x097F for ch in text)


def is_tamil(text: str) -> bool:
    return any(0x0B80 <= ord(ch) <= 0x0BFF for ch in text)


def is_kannada(text: str) -> bool:
    return any(0x0C80 <= ord(ch) <= 0x0CFF for ch in text)


# Map target_lang → script checker
LANG_TO_SCRIPT = {
    "te": is_telugu,
    "hi": is_hindi,
    "ta": is_tamil,
    "kn": is_kannada,
}


def is_in_target_script(text: str, lang: str) -> bool:
    fn = LANG_TO_SCRIPT.get(lang)
    if not fn:
        return False
    return fn(text)
