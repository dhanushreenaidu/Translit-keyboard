// frontend/src/components/typing/TypingArea.tsx

import React, { useEffect, useState } from "react";
import {
  transliterateText,
  detectLanguage,
  type TransliterationCandidate,
  type LanguageDetectResponse,
} from "../../utils/api";

interface TypingAreaProps {
  targetLang: string;
  mode: "native" | "mix";
  onOutputChange: (output: string) => void;
  onInputChange: (input: string) => void;
}

const TypingArea: React.FC<TypingAreaProps> = ({
  targetLang,
  mode,
  onOutputChange,
  onInputChange,
}) => {
  const [input, setInput] = useState("");
  const [output, setOutput] = useState("");
  const [candidates, setCandidates] = useState<TransliterationCandidate[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 🎙 STT state
  const [listening, setListening] = useState(false);

  // 🔍 Language detection state
  const [detected, setDetected] = useState<LanguageDetectResponse | null>(null);
  const [detectError, setDetectError] = useState<string | null>(null);

  // 🔤 Full QWERTY layout (3 rows) + special keys
  const keyboardRows: string[][] = [
    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
    ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
    ["Z", "X", "C", "V", "B", "N", "M"],
  ];
  const specialKeys = ["Space", "Backspace"];

  // 🔁 Transliteration effect
  useEffect(() => {
    const text = input.trim();
    if (!text) {
      setOutput("");
      setCandidates([]);
      setError(null);
      onOutputChange("");
      return;
    }

    let cancelled = false;

    const run = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await transliterateText(text, targetLang, mode);
        if (cancelled) return;

        setOutput(res.primary);
        setCandidates(res.candidates || []);
        onOutputChange(res.primary);
      } catch (err) {
        console.error(err);
        if (!cancelled) {
          setError("Failed to transliterate");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    void run();

    return () => {
      cancelled = true;
    };
  }, [input, targetLang, mode, onOutputChange]);

  // 🔁 Language detection effect (debounced)
  useEffect(() => {
    const text = input.trim();
    if (!text) {
      setDetected(null);
      setDetectError(null);
      return;
    }

    let cancelled = false;
    const timeout = setTimeout(() => {
      const runDetect = async () => {
        try {
          const res = await detectLanguage(text);
          if (!cancelled) {
            setDetected(res);
            setDetectError(null);
          }
        } catch (err) {
          console.error(err);
          if (!cancelled) {
            setDetectError("Lang detect failed");
          }
        }
      };
      void runDetect();
    }, 250); // small debounce

    return () => {
      cancelled = true;
      clearTimeout(timeout);
    };
  }, [input]);

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    setInput(value);
    onInputChange(value);
  };

  const handleCandidateClick = (cand: TransliterationCandidate) => {
    setOutput(cand.text);
    onOutputChange(cand.text);
  };

  const handleKeyClick = (key: string) => {
    let newText = input;

    if (key === "Space") {
      newText = input + " ";
    } else if (key === "Backspace") {
      newText = input.slice(0, -1);
    } else {
      newText = input + key.toLowerCase();
    }

    setInput(newText);
    onInputChange(newText);
  };

  // 🎙️ STT: Web Speech API
  const handleMicClick = () => {
    if (typeof window === "undefined") {
      alert("STT not supported in this environment.");
      return;
    }

    const SpeechRecognition =
      (window as any).SpeechRecognition ||
      (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert("Your browser does not support Speech Recognition.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-IN";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      setListening(true);
    };

    recognition.onend = () => {
      setListening(false);
    };

    recognition.onerror = (event: any) => {
      console.error("STT error:", event.error);
      setListening(false);
      alert("Speech recognition error: " + event.error);
    };

    recognition.onresult = (event: any) => {
      const transcript: string = event.results[0][0].transcript;
      console.log("STT transcript:", transcript);

      const newText = (input + " " + transcript).trim();
      setInput(newText);
      onInputChange(newText);
    };

    recognition.start();
  };

  const detectedLabel =
    detected && detected.language !== "unknown"
      ? `${detected.language} (${detected.script}) · ${(
          detected.confidence * 100
        ).toFixed(0)}%`
      : "unknown";

  return (
    <div className="space-y-3">
      {/* Top row: label + detected language badge */}
      <div className="flex items-center justify-between text-xs">
        <span className="text-slate-400">Typing Area</span>
        <span className="text-[11px] px-2 py-0.5 rounded-full bg-slate-900 border border-slate-700 text-slate-300">
          Detected: {detectError ? "error" : detectedLabel}
        </span>
      </div>

      {/* Input textarea */}
      <textarea
        className="w-full h-32 rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-50 outline-none focus:ring-2 focus:ring-indigo-500"
        placeholder="Type in English... e.g., namaste"
        value={input}
        onChange={handleChange}
      />

      {/* Output display */}
      <div className="bg-slate-900 border border-slate-700 rounded-lg p-3 min-h-[3rem] text-lg">
        {loading ? (
          <span className="text-slate-400 text-sm">Transliterating…</span>
        ) : (
          <span>{output}</span>
        )}
      </div>

      {/* Candidates */}
      <div className="flex flex-wrap gap-2 text-xs">
        {candidates.map((cand, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => handleCandidateClick(cand)}
            className="px-3 py-1 rounded-full bg-slate-800 hover:bg-slate-700 border border-slate-700"
          >
            {cand.text}
          </button>
        ))}
      </div>

      {error && <div className="text-xs text-red-400">{error}</div>}

      {/* Virtual keyboard + mic */}
      <div className="mt-2 bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs text-slate-400">
            Virtual keyboard (placeholder – physical keyboard still works)
          </span>

          <button
            type="button"
            onClick={handleMicClick}
            className={`flex items-center gap-1 px-3 py-1.5 rounded-full text-xs border ${
              listening
                ? "bg-red-600 border-red-500 text-white"
                : "bg-slate-800 border-slate-700 text-slate-100"
            }`}
          >
            {listening ? "🎙 Listening..." : "🎙 Start mic"}
          </button>
        </div>

        {/* QWERTY rows */}
        <div className="space-y-2">
          {keyboardRows.map((row, rowIdx) => (
            <div key={rowIdx} className="flex justify-center gap-2">
              {row.map((key) => (
                <button
                  key={key}
                  type="button"
                  onClick={() => handleKeyClick(key)}
                  className="w-10 h-10 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-sm"
                >
                  {key}
                </button>
              ))}
            </div>
          ))}

          {/* Special keys */}
          <div className="flex justify-center gap-2 pt-1">
            {specialKeys.map((key) => (
              <button
                key={key}
                type="button"
                onClick={() => handleKeyClick(key)}
                className={`h-10 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs px-4 ${
                  key === "Space" ? "w-40" : "w-24"
                }`}
              >
                {key}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TypingArea;
