import { FileSearch } from "lucide-react";
import type { CitationSource } from "@/types/rag.types";

const TYPE_LABEL: Record<CitationSource["type"], string> = {
  dataset_profile: "Dataset Profile",
  cleaning_log: "Cleaning Log",
  analytics_summary: "Analytics Summary",
  forecast_summary: "Forecast Summary",
  decision_recommendation: "Decision Recommendation",
  executive_summary: "Executive Summary",
  conversation_history: "Prior Conversation",
};

export function CitationSourceCard({ source }: { source: CitationSource }) {
  return (
    <div className="rounded-xl border border-line bg-bg-surface/60 p-3">
      <div className="mb-1 flex items-center justify-between">
        <span className="flex items-center gap-1.5 text-[11px] font-mono uppercase tracking-wide text-signal">
          <FileSearch className="h-3 w-3" />
          {TYPE_LABEL[source.type]}
        </span>
        <span className="font-mono text-[10px] text-ink-faint">
          {Math.round(source.relevanceScore * 100)}% match
        </span>
      </div>
      <p className="text-xs font-medium text-ink">{source.title}</p>
      <p className="mt-1 text-xs text-ink-muted">{source.snippet}</p>
    </div>
  );
}
