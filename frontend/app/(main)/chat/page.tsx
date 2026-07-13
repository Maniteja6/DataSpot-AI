"use client";

import { useDatasets } from "@/features/datasets/hooks/useDatasets";
import { ChatWindow } from "@/features/chat-assistant/components/ChatWindow";
import { Badge } from "@/components/ui/badge";
import { Sparkles } from "lucide-react";

export default function ChatPage() {
  const { data: datasets } = useDatasets();
  const activeDataset = datasets?.[0];

  return (
    <div className="animate-fade-up space-y-3">
      <div className="flex items-center justify-between">
        <p className="text-sm text-ink-muted">
          Grounded in{" "}
          <span className="text-ink">{activeDataset?.name ?? "no dataset yet"}</span>
        </p>
        <Badge variant="signal">
          <Sparkles className="h-3 w-3" /> RAG-grounded
        </Badge>
      </div>
      <ChatWindow datasetId={activeDataset?.id} />
    </div>
  );
}
