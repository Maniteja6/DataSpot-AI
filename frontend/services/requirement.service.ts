import { apiClient, withMockFallback } from "./api-client";
import { mockRequirementRun, mockRequirementHistory } from "./mocks/mockData";
import type { RequirementRun } from "@/types/requirement.types";

export const requirementService = {
  submit: (datasetId: string, requirement: string) =>
    withMockFallback(
      () =>
        apiClient.post<RequirementRun>(
          "/api/v1/requirements",
          { datasetId, requirement },
          { timeoutMs: 45000 }
        ),
      () => mockRequirementRun(datasetId, requirement)
    ),

  listByDataset: (datasetId: string) =>
    withMockFallback(
      () => apiClient.get<RequirementRun[]>(`/api/v1/requirements?datasetId=${datasetId}`),
      () => mockRequirementHistory(datasetId)
    ),
};
