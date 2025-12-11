// frontend/src/components/ModelMetrics.tsx

import React from "react";

type LangMetric = {
  langCode: string;
  name: string;
  acc: number; // exact-match accuracy
  cer: number; // character error rate
  samples: number;
};

const METRICS: LangMetric[] = [
  {
    langCode: "hi",
    name: "Hindi",
    acc: 0.504,
    cer: 0.1171,
    samples: 500,
  },
  {
    langCode: "te",
    name: "Telugu",
    acc: 0.74,
    cer: 0.0435,
    samples: 500,
  },
  {
    langCode: "ta",
    name: "Tamil",
    acc: 0.804,
    cer: 0.029,
    samples: 500,
  },
  {
    langCode: "kn",
    name: "Kannada",
    acc: 0.804,
    cer: 0.1027,
    samples: 500,
  },
  {
    langCode: "ml",
    name: "Malayalam",
    acc: 0.804,
    cer: 0.0817,
    samples: 500,
  },
  // You can add more later
];

const ModelMetrics: React.FC = () => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 text-sm space-y-3">
      <div className="flex items-center justify-between gap-2">
        <h3 className="font-semibold text-slate-100">Model metrics</h3>
        <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 whitespace-nowrap">
          Evaluated via /api/transliterate
        </span>
      </div>

      <p className="text-xs text-slate-400">
        Exact-match accuracy and character error rate (CER) on 500 validation
        samples from the Aksharantar dataset. Lower CER is better.
      </p>

      <div className="space-y-2 max-h-40 overflow-y-auto pr-1">
        {METRICS.map((m) => (
          <div
            key={m.langCode}
            className="flex items-center justify-between bg-slate-950/60 rounded-lg px-3 py-2"
          >
            <div>
              <div className="text-xs font-medium">
                {m.name}{" "}
                <span className="text-[10px] text-slate-400">
                  ({m.langCode})
                </span>
              </div>
              <div className="text-[11px] text-slate-400">
                {m.samples} samples · CER {m.cer.toFixed(3)}
              </div>
            </div>

            <div className="text-right">
              <div className="text-xs text-slate-300">
                Acc{" "}
                <span className="font-semibold">
                  {(m.acc * 100).toFixed(1)}%
                </span>
              </div>
              <div className="text-[10px] text-slate-500">
                (1 epoch / small seq2seq)
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ModelMetrics;
