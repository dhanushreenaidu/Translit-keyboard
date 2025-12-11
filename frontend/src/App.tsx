// frontend/src/App.tsx

import React, { useState } from "react";
import TypingArea from "./components/typing/TypingArea";
import ChatPanel from "./components/chat/ChatPanel";
import ModelMetrics from "./components/ModelMetrics";

function App() {
  const [targetLang, setTargetLang] = useState("hi");
  const [mode, setMode] = useState<"native" | "mix">("native");

  const [lastOutput, setLastOutput] = useState("");
  const [rawInput, setRawInput] = useState("");

  // ---- TTS Handler (browser Web Speech) ----
  // ---- TTS Handler (browser Web Speech) ----
  const handleSpeak = () => {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) {
      alert("Browser does not support TTS.");
      return;
    }

    // ✅ Decide *what* to speak (different for hi vs others)
    const textToSpeak =
      targetLang === "hi"
        ? (lastOutput || rawInput || "").trim() // Hindi → prefer native script
        : (rawInput || lastOutput || "").trim(); // Others → prefer English input

    if (!textToSpeak) {
      alert("Nothing to speak yet!");
      return;
    }

    const synth = window.speechSynthesis;
    const utterance = new SpeechSynthesisUtterance(textToSpeak);

    // ✅ Voice / language selection
    if (targetLang === "hi") {
      // Try Hindi voice if browser has it
      utterance.lang = "hi-IN";
      const voices = synth.getVoices();
      const hiVoice = voices.find((v) => v.lang === "hi-IN");
      if (hiVoice) utterance.voice = hiVoice;
    } else {
      // Telugu / Tamil / others → English Indian or US voice
      const voices = synth.getVoices();
      const enIn =
        voices.find((v) => v.lang === "en-IN") ||
        voices.find((v) => v.lang === "en-US");
      if (enIn) {
        utterance.voice = enIn;
        utterance.lang = enIn.lang;
      } else {
        utterance.lang = "en-US";
      }
    }

    synth.cancel();
    synth.speak(utterance);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* ---- Header ---- */}
        <header className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div className="space-y-1">
            <h1 className="text-2xl md:text-3xl font-bold tracking-tight">
              TransKey — ML Keyboard
            </h1>
            <p className="text-xs md:text-sm text-slate-400">
              ML-powered transliteration keyboard for Indian languages.
            </p>

            <div className="flex flex-wrap gap-2 mt-2">
              <span className="text-[11px] px-2 py-0.5 rounded-full bg-slate-900 border border-slate-700">
                Model: PyTorch seq2seq (hi, te, ta…)
              </span>
              <span className="text-[11px] px-2 py-0.5 rounded-full bg-emerald-900/40 text-emerald-300 border border-emerald-700">
                ML-powered
              </span>
            </div>
          </div>

          {/* ---- Controls ---- */}
          <div className="flex flex-col sm:flex-row items-center gap-3">
            {/* Language Selector */}
            <select
              className="bg-slate-900 border border-slate-700 px-3 py-2 rounded-lg text-sm"
              value={targetLang}
              onChange={(e) => setTargetLang(e.target.value)}
            >
              <option value="hi">Hindi (hi)</option>
              <option value="te">Telugu (te)</option>
              <option value="ta">Tamil (ta)</option>
              <option value="kn">Kannada (kn)</option>
              <option value="ml">Malayalam (ml)</option>
              <option value="mr">Marathi (mr)</option>
              <option value="gu">Gujarati (gu)</option>
              <option value="bn">Bengali (bn)</option>
              <option value="pa">Punjabi (pa)</option>
            </select>

            {/* Mode Selector */}
            <select
              className="bg-slate-900 border border-slate-700 px-3 py-2 rounded-lg text-sm"
              value={mode}
              onChange={(e) => setMode(e.target.value as "native" | "mix")}
            >
              <option value="native">Native Mode</option>
              <option value="mix">Mix Mode</option>
            </select>

            {/* TTS Button */}
            <button
              onClick={handleSpeak}
              className="bg-indigo-600 hover:bg-indigo-700 px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-1"
            >
              🔊 Speak
            </button>
          </div>
        </header>

        {/* ---- Main 2-column area ---- */}
        <main className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left: Typing + virtual keyboard + mic */}
          <section>
            <TypingArea
              targetLang={targetLang}
              mode={mode}
              onOutputChange={setLastOutput}
              onInputChange={setRawInput}
            />
          </section>

          {/* Right: Assistant chat */}
          <section className="h-full">
            <ChatPanel language={targetLang} />
          </section>
        </main>

        {/* ---- Bottom: How it works + Metrics ---- */}
        <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* How it works */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 text-sm space-y-2">
            <h2 className="font-semibold text-slate-100">
              How it works (ML pipeline)
            </h2>
            <ol className="list-decimal list-inside space-y-1 text-slate-300 text-xs md:text-sm">
              <li>
                You type in English (e.g.{" "}
                <span className="italic">"nenu Hyderabad ki vasthunna"</span>).
              </li>
              <li>
                The text is sent to the FastAPI backend:{" "}
                <code className="px-1 py-0.5 bg-slate-800 rounded text-[11px]">
                  POST /api/transliterate
                </code>
              </li>
              <li>
                The backend loads a{" "}
                <span className="font-semibold">
                  PyTorch seq2seq transliteration model
                </span>{" "}
                trained on the Aksharantar dataset (hi, te, ta…).
              </li>
              <li>
                The model outputs the native-script text plus candidate
                suggestions.
              </li>
              <li>
                The browser shows the output in real time and can use Web Speech
                API for TTS and Web Speech Recognition for STT.
              </li>
              <li>
                The assistant panel talks to the Python backend, which calls the
                Gemini API for chat responses.
              </li>
            </ol>
          </div>

          {/* Metrics card */}
          <ModelMetrics />
        </section>
      </div>
    </div>
  );
}

export default App;
