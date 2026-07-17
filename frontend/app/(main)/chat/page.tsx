"use client";

import { useState } from "react";
import { useDatasets } from "@/features/datasets/hooks/useDatasets";
import { ChatWindow } from "@/features/chat-assistant/components/ChatWindow";
import { DatasetPicker } from "@/components/shared/DatasetPicker";
import { Badge } from "@/components/ui/badge";
import { Sparkles } from "lucide-react";

export default function ChatPage() {
  const { data: datasets } = useDatasets();
  const [selectedDatasetId, setSelectedDatasetId] = useState<string | null>(null);
  const datasetId = selectedDatasetId ?? datasets?.[0]?.id ?? null;

  return (
    <div className="animate-fade-up space-y-3">
      <div className="flex items-center justify-between">
        <DatasetPicker value={datasetId} onChange={setSelectedDatasetId} />
        <Badge variant="signal">
          <Sparkles className="h-3 w-3" /> RAG-grounded
        </Badge>
      </div>
      <ChatWindow datasetId={datasetId ?? undefined} />
    </div>
  );
}
