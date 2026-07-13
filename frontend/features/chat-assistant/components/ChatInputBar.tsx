"use client";

import { useState } from "react";
import { Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export function ChatInputBar({ onSend, disabled }: { onSend: (text: string) => void; disabled?: boolean }) {
  const [value, setValue] = useState("");

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!value.trim()) return;
    onSend(value);
    setValue("");
  }

  return (
    <form onSubmit={handleSubmit} className="flex items-center gap-2 border-t border-line pt-3">
      <Input
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Ask about trends, anomalies, forecasts, or recommendations…"
        disabled={disabled}
      />
      <Button type="submit" size="icon" disabled={disabled || !value.trim()}>
        <Send className="h-4 w-4" />
      </Button>
    </form>
  );
}
