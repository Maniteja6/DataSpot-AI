"use client";

import { useQuery } from "@tanstack/react-query";
import { queryKeys } from "@/lib/react-query/queryKeys";
import { mockPipelineStages, mockAgentActivity } from "@/services/mocks/mockData";

// In production this polls GET /api/v1/agents/pipeline-status?datasetId=
// via agents_controller.py, which reports live AgentCore agent/orchestrator state.
export function usePipelineStatus(datasetId: string | null) {
  return useQuery({
    queryKey: queryKeys.pipeline.status(datasetId ?? "none"),
    queryFn: async () => ({
      stages: mockPipelineStages,
      activity: mockAgentActivity,
    }),
    enabled: !!datasetId,
    refetchInterval: (query) => {
      const stillRunning = query.state.data?.stages.some(
        (s) => s.status === "running" || s.status === "queued"
      );
      return stillRunning ? 4000 : false;
    },
  });
}
