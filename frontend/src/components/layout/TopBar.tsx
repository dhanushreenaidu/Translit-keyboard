  import React from "react";

  export const TopBar: React.FC = () => {
    return (
      <header className="w-full px-4 py-3 border-b border-slate-800 bg-slate-900/80 backdrop-blur flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-lg font-semibold">TransKey ML</span>
          <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-500/40">
            ML-powered
          </span>
        </div>

        <div className="flex items-center gap-3">
          <select className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-1 text-sm">
            <option value="te">Telugu (te)</option>
            <option value="hi">Hindi (hi)</option>
            <option value="ta">Tamil (ta)</option>
            <option value="kn">Kannada (kn)</option>
            <option value="ml">Malayalam (ml)</option>
            <option value="mr">Marathi (mr)</option>
            <option value="bn">Bengali (bn)</option>
            <option value="gu">Gujarati (gu)</option>
            <option value="pa">Punjabi (pa)</option>
          </select>

          <button className="text-xs px-3 py-1 rounded-full border border-slate-600 bg-slate-900 hover:bg-slate-800 transition">
            Mode: Native
          </button>
        </div>
      </header>
    );
  };
