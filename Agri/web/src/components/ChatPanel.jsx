import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import api from "../api.js";

function AssistantMessage({ content }) {
  return (
    <div className="chat-markdown prose prose-sm max-w-none prose-headings:font-serif prose-headings:text-leafdeep prose-p:my-2 prose-ul:my-2 prose-ol:my-2 prose-li:my-0 prose-strong:text-leafdeep prose-a:text-leaf">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          table: ({ children }) => (
            <div className="my-3 overflow-x-auto rounded-lg border border-[#d9cbb3]">
              <table className="min-w-full text-left text-xs">{children}</table>
            </div>
          ),
          th: ({ children }) => <th className="bg-[#efe6d6] px-3 py-2 font-bold">{children}</th>,
          td: ({ children }) => <td className="border-t border-[#e5dac7] px-3 py-2 align-top">{children}</td>,
          code: ({ children, className }) => (
            <code className={className || "rounded bg-[#efe6d6] px-1 py-0.5 text-xs"}>{children}</code>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}

export default function ChatPanel({ compact = false }) {
  const [message, setMessage] = useState("");
  const [history, setHistory] = useState([]);
  const [busy, setBusy] = useState(false);

  async function send(e) {
    e.preventDefault();
    const text = message.trim();
    if (!text || busy) return;
    const prior = history;
    const next = [...prior, { role: "user", content: text }];
    setHistory(next);
    setMessage("");
    setBusy(true);
    try {
      const { data } = await api.post("/chatbot/ask", { message: text, history: prior });
      setHistory([...next, { role: "assistant", content: data.answer }]);
    } catch (err) {
      setHistory([
        ...next,
        { role: "assistant", content: err.response?.data?.detail || "Chat request failed." },
      ]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className={`flex flex-col ${compact ? "h-80" : "h-[70vh]"}`}>
      {!compact && <h2 className="font-serif text-2xl">AI Assistant</h2>}
      <div className="flex-1 overflow-auto mt-2 space-y-2 text-sm">
        {history.length === 0 && (
          <p className="text-[#6b5d4d]">Ask about your farm, soil, or latest model results.</p>
        )}
        {history.map((m, i) => (
          <div
            key={i}
            className={`rounded-xl px-3 py-2 ${m.role === "user" ? "bg-straw ml-8" : "bg-emerald-50 mr-8"}`}
          >
              {m.role === "assistant" ? <AssistantMessage content={m.content} /> : m.content}
          </div>
        ))}
      </div>
      <form className="mt-3 flex gap-2" onSubmit={send}>
        <input
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Ask about your farm…"
        />
        <button disabled={busy} className="rounded-xl bg-leafdeep text-white px-4 font-bold disabled:opacity-50">
          Send
        </button>
      </form>
    </div>
  );
}
