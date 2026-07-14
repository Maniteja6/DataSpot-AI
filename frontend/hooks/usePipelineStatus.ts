"use client";

import { useQuery } from "@tanstack/react-query";
import { queryKeys } from "@/lib/react-query/queryKeys";
import { agentsService } from "@/services/agents.service";

// Polls GET /api/v1/agents/pipeline-status?datasetId= via agents_controller.py,
// which reports live LangGraph pipeline / AgentCore agent state. Falls back
// to generated mock data automatically when NEXT_PUBLIC_USE_MOCKS=true or if
// the backend call fails (see services/agents.service.ts).
export function usePipelineStatus(datasetId: string | null) {
  return useQuery({
    queryKey: queryKeys.pipeline.status(datasetId ?? "none"),
    queryFn: () => agentsService.getPipelineStatus(datasetId as string),
    enabled: !!datasetId,
    refetchInterval: (query) => {
      const stillRunning = query.state.data?.stages.some(
        (s) => s.status === "running" || s.status === "queued"
      );
      return stillRunning ? 4000 : false;
    },
  });
}