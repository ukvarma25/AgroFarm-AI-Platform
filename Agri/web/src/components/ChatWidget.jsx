import { useState } from "react";
import ChatPanel from "./ChatPanel.jsx";

export default function ChatWidget() {
  const [open, setOpen] = useState(false);
  return (
    <div className="fixed bottom-5 right-5 z-50">
      {open && (
        <div className="mb-3 w-[min(22rem,calc(100vw-2.5rem))] card shadow-xl">
          <div className="flex items-center justify-between mb-1">
            <p className="font-serif text-lg">Farm chatbot</p>
            <button className="text-sm text-[#6b5d4d]" onClick={() => setOpen(false)}>
              Close
            </button>
          </div>
          <ChatPanel compact />
        </div>
      )}
      <button
        onClick={() => setOpen((v) => !v)}
        className="ml-auto flex h-12 w-12 items-center justify-center rounded-full bg-leafdeep text-white shadow-lg"
        aria-label="Open chatbot"
      >
        AI
      </button>
    </div>
  );
}
