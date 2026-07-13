import { create } from "zustand";
import type { ChatMessage } from "@/types/api.types";

interface ChatState {
  messages: ChatMessage[];
  isStreaming: boolean;
  addMessage: (message: ChatMessage) => void;
  setStreaming: (streaming: boolean) => void;
  clearConversation: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [
    {
      id: "welcome",
      role: "assistant",
      content:
        "I'm your DataSpot analyst. Upload a dataset and I'll ground every answer in its actual profile, cleaning log, and forecasts — with sources cited.",
      createdAt: new Date().toISOString(),
    },
  ],
  isStreaming: false,
  addMessage: (message) =>
    set((state) => ({ messages: [...state.messages, message] })),
  setStreaming: (streaming) => set({ isStreaming: streaming }),
  clearConversation: () => set({ messages: [] }),
}));
