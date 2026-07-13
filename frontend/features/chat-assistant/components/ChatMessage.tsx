import { Bot, User } from "lucide-react";
import { cn } from "@/utils/cn";
import { RetrievedContextDrawer } from "./RetrievedContextDrawer";
import type { ChatMessage as ChatMessageType } from "@/types/api.types";

export function ChatMessage({ message }: { message: ChatMessageType }) {
  const isUser = message.role === "user";

  return (
    <div className={cn("flex gap-3", isUser && "flex-row-reverse")}>
      <div
        className={cn(
          "flex h-8 w-8 shrink-0 items-center justify-center rounded-full",
          isUser ? "bg-bg-raised text-ink-muted" : "bg-signal-soft text-signal"
        )}
      >
        {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
      </div>
      <div className={cn("max-w-[75%] rounded-2xl px-4 py-2.5 text-sm", isUser ? "bg-bg-raised text-ink" : "glass-panel text-ink-muted")}>
        <p>{message.content}</p>
        {message.citations && <RetrievedContextDrawer citations={message.citations} />}
      </div>
    </div>
  );
}
