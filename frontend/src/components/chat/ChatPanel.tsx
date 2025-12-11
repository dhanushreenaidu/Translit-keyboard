// frontend/src/components/chat/ChatPanel.tsx

import React, { useState } from "react";
import type { ChatMessage, ChatResponse } from "../../utils/api";
import { sendChat } from "../../utils/api";

interface ChatPanelProps {
  language: string; // "hi", "te", etc.
}

const ChatPanel: React.FC<ChatPanelProps> = ({ language }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content:
        "Hi! I'm your TransKey assistant. Ask me something or just say hi.",
    },
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastProvider, setLastProvider] = useState<string | null>(null);

  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed || loading) return;

    const newMessages: ChatMessage[] = [
      ...messages,
      { role: "user", content: trimmed },
    ];
    setMessages(newMessages);
    setInput("");
    setLoading(true);
    setError(null);

    try {
      const res: ChatResponse = await sendChat(newMessages, language);
      setMessages([...newMessages, { role: "assistant", content: res.reply }]);
      setLastProvider(res.provider);
    } catch (err) {
      console.error(err);
      setError("Failed to get reply from assistant.");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="bg-slate-900 rounded-xl p-4 border border-slate-700 flex flex-col h-[360px] lg:h-[420px]">
      <div className="flex items-center justify-between mb-3">
        <h2 className="font-semibold text-lg">Assistant</h2>
        {lastProvider && (
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-300">
            Provider: {lastProvider}
          </span>
        )}
      </div>

      {/* Messages – scrollable area */}
      <div className="flex-1 bg-slate-800 rounded-lg p-3 text-sm overflow-y-auto space-y-2">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`max-w-[80%] px-3 py-2 rounded-lg ${
              m.role === "user"
                ? "ml-auto bg-indigo-600 text-white"
                : "mr-auto bg-slate-700 text-slate-50"
            }`}
          >
            {m.content}
          </div>
        ))}

        {loading && (
          <div className="mr-auto text-xs text-slate-400">Thinking…</div>
        )}
      </div>

      {/* Error */}
      {error && <div className="text-xs text-red-400 mt-1">{error}</div>}

      {/* Input */}
      <div className="mt-3 flex gap-2">
        <textarea
          className="flex-1 rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-xs text-slate-50 outline-none focus:ring-2 focus:ring-indigo-500"
          rows={2}
          placeholder="Ask something about the keyboard, ML, or just say hi…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button
          type="button"
          onClick={handleSend}
          disabled={loading || !input.trim()}
          className="self-end px-4 py-2 rounded-lg bg-indigo-600 text-xs font-medium disabled:opacity-50"
        >
          {loading ? "Sending..." : "Send"}
        </button>
      </div>
    </div>
  );
};

export default ChatPanel;
