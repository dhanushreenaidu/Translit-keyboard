// frontend/src/utils/api.ts

// ---------- Types ----------

export type TransliterationCandidate = {
  text: string;
  score?: number | null;
};

export type TransliterationResponse = {
  input_text: string;
  primary: string;
  candidates: TransliterationCandidate[];
  source_lang: string;
  target_lang: string;
  mode: string;
  provider: string;
};

export type LanguageDetectResponse = {
  text: string;
  language: string; // "hi", "te", "ta", "en", "mixed", "unknown"
  script: string;
  confidence: number;
};

export type ChatRole = "user" | "assistant";

export type ChatMessage = {
  role: ChatRole;
  content: string;
};

export type ChatResponse = {
  reply: string;
  provider: string;
};

// ---------- Backend base URL ----------

const BACKEND_URL = "http://localhost:8000"; // or 127.0.0.1:8000, both ok

// ---------- Transliteration API ----------

export async function transliterateText(
  text: string,
  targetLang: string,
  mode: "native" | "mix" = "native"
): Promise<TransliterationResponse> {
  const res = await fetch(`${BACKEND_URL}/api/transliterate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      text,
      source_lang: "en",
      target_lang: targetLang,
      mode,
    }),
  });

  if (!res.ok) {
    throw new Error(`HTTP ${res.status}`);
  }

  return res.json();
}

// ---------- Language detection API ----------

export async function detectLanguage(
  text: string
): Promise<LanguageDetectResponse> {
  const res = await fetch(`${BACKEND_URL}/api/detect-language`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });

  if (!res.ok) {
    throw new Error(`HTTP ${res.status}`);
  }

  return res.json();
}

// ---------- Backend TTS helper (optional) ----------

export async function ttsSpeak(text: string, lang: string): Promise<void> {
  if (!text.trim()) {
    throw new Error("Nothing to speak");
  }

  const res = await fetch(`${BACKEND_URL}/api/tts`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, lang }),
  });

  if (!res.ok) {
    throw new Error(`TTS HTTP ${res.status}`);
  }

  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const audio = new Audio(url);
  audio.play();
}

// ---------- Chat API ----------

export async function sendChat(
  messages: ChatMessage[],
  language: string
): Promise<ChatResponse> {
  const res = await fetch(`${BACKEND_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages, language }),
  });

  if (!res.ok) {
    throw new Error(`Chat HTTP ${res.status}`);
  }

  return res.json();
}
