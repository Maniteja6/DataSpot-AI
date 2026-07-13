"use client";

import { useState, useCallback } from "react";
import { chatService } from "@/services/chat.service";
import { useChatStore } from "@/stores/useChatStore";

export function useRagChat(datasetId?: string) {
  const { messages, addMessage, isStreaming, setStreaming } = useChatStore();
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(
    async (question: string) => {
      if (!question.trim()) return;
      setError(null);

      addMessage({
        id: `u_${Date.now()}`,
        role: "user",
        content: question,
        createdAt: new Date().toISOString(),
      });

      setStreaming(true);
      try {
        const result = await chatService.ask(question, datasetId);
        addMessage({
          id: `a_${Date.now()}`,
          role: "assistant",
          content: result.answer,
          citations: result.citations,
          createdAt: new Date().toISOString(),
        });
      } catch (err) {
        setError("The analyst couldn't reach the backend. Try again in a moment.");
      } finally {
        setStreaming(false);
      }
    },
    [datasetId, addMessage, setStreaming]
  );

  return { messages, sendMessage, isStreaming, error };
}
