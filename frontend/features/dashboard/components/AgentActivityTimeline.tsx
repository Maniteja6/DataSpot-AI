"use client";

import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { AgentStatusPill } from "@/components/shared/AgentStatusPill";
import { formatRelativeTime } from "@/lib/formatters";
import { useAgentStream } from "@/hooks/useAgentStream";
import { usePipelineStatus } from "@/hooks/usePipelineStatus";

const AGENT_LABEL: Record<string, string> = {
  dataset_understanding: "Dataset Understanding",
  data_cleaning: "Data Cleaning",
  analytics: "Analytics",
  predictive_analytics: "Predictive Analytics",
  business_intelligence: "Business Intelligence",
  decision_support: "Decision Support",
  executive_summary: "Executive Summary",
  rag_chat: "RAG Chat",
};

interface AgentActivityTimelineProps {
  /** When provided, shows real pipeline activity for this dataset (polling
   * the backend). When omitted, falls back to a simulated feed so the
   * Dashboard doesn't look empty before anything's been uploaded. */
  datasetId?: string;
}

export function AgentActivityTimeline({ datasetId }: AgentActivityTimelineProps) {
  const pipelineStatus = usePipelineStatus(datasetId ?? null);
  const simulatedActivity = useAgentStream();

  const activity = datasetId ? pipelineStatus.data?.activity ?? [] : simulatedActivity;

  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>AI Activity Timeline</CardTitle>
          <CardDescription>Live status from Bedrock AgentCore agents</CardDescription>
        </div>
      </CardHeader>
      <div className="space-y-4">
        {activity.length === 0 && (
          <p className="text-sm text-ink-faint">No agent activity yet — upload a dataset to see the pipeline run.</p>
        )}
        {activity.map((a, i) => (
          <div key={a.id} className="relative flex gap-3 pl-1">
            <div className="flex flex-col items-center">
              <span className="h-2 w-2 rounded-full bg-signal" />
              {i < activity.length - 1 && <span className="mt-1 h-full w-px bg-line" />}
            </div>
            <div className="flex-1 pb-4">
              <div className="flex items-center justify-between gap-2">
                <p className="text-xs font-mono uppercase tracking-wide text-ink-faint">
                  {AGENT_LABEL[a.agent] ?? a.agent}
                </p>
                <AgentStatusPill status={a.status} />
              </div>
              <p className="mt-0.5 text-sm text-ink-muted">{a.label}</p>
              <p className="mt-0.5 text-[11px] text-ink-faint">{formatRelativeTime(a.startedAt)}</p>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}