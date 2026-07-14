import { apiClient, withMockFallback } from "./api-client";
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
};