"use client";

import { useEffect, useRef } from "react";
import { useRagChat } from "../hooks/useRagChat";
import { ChatMessage } from "./ChatMessage";
import { ChatInputBar } from "./ChatInputBar";

export function ChatWindow({ datasetId }: { datasetId?: string }) {
  const { messages, sendMessage, isStreaming, error } = useRagChat(datasetId);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex h-[calc(100vh-11rem)] flex-col rounded-2xl border border-line bg-bg-surface/40 p-4">
      <div className="flex-1 space-y-4 overflow-y-auto pr-1">
        {messages.map((m) => (
          <ChatMessage key={m.id} message={m} />
        ))}
        {isStreaming && (
          <p className="pl-11 text-xs text-ink-faint">Retrieving grounded context…</p>
        )}
        {error && <p className="pl-11 text-xs text-rose">{error}</p>}
        <div ref={bottomRef} />
      </div>
      <ChatInputBar onSend={sendMessage} disabled={isStreaming} />
    </div>
  );
}
