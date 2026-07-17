import { apiClient, withMockFallback, ApiClientError } from "./api-client";
import { mockPipelineStages, mockAgentActivity } from "./mocks/mockData";
import type { PipelineStage, AgentActivity } from "@/types/agent.types";

export interface PipelineStatusResponse {
  stages: PipelineStage[];
  activity: AgentActivity[];
}

export const agentsService = {
  getPipelineStatus: (datasetId: string) =>
    withMockFallback(
      () => apiClient.get<PipelineStatusResponse>(`/api/v1/agents/pipeline-status?datasetId=${datasetId}`),
      () => ({ stages: mockPipelineStages, activity: mockAgentActivity })
    ),

  /**
   * Bypasses the mock fallback — pipeline status is in-memory only on the
   * backend and doesn't survive a restart, so a 404 here just means "no
   * tracked history," not "backend unreachable." Used wherever showing a
   * real empty state matters more than graceful degradation to mock data.
   */
  getPipelineStatusSafe: async (datasetId: string): Promise<PipelineStatusResponse | null> => {
    try {
      return await apiClient.get<PipelineStatusResponse>(`/api/v1/agents/pipeline-status?datasetId=${datasetId}`);
    } catch (err) {
      if (err instanceof ApiClientError && err.status === 404) return null;
      throw err;
    }
  },
};