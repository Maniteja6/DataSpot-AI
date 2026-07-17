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

/**
 * Like usePipelineStatus, but never falls back to mock data on a 404 — used
 * where a real empty state matters more than graceful degradation (e.g. the
 * Dashboard's activity feed, which otherwise showed fake sample-dataset
 * activity for real datasets with no tracked pipeline history).
 */
export function usePipelineStatusSafe(datasetId: string | null) {
  return useQuery({
    queryKey: [...queryKeys.pipeline.status(datasetId ?? "none"), "safe"],
    queryFn: () => agentsService.getPipelineStatusSafe(datasetId as string),
    enabled: !!datasetId,
  });
}