import React from "react";

export const STTButton: React.FC = () => {
  return (
    <button className="inline-flex items-center gap-1 px-3 py-1.5 rounded-full border border-slate-700 bg-slate-900 hover:bg-slate-800 text-xs transition">
      <span>🎙️</span>
      <span>STT (Phase 6)</span>
    </button>
  );
};
