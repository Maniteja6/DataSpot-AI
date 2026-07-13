import { apiClient, withMockFallback } from "./api-client";
import { mockPredictiveRun } from "./mocks/mockData";
import type { PredictiveRun } from "@/types/prediction.types";

export const predictiveService = {
  getRun: (datasetId: string) =>
    withMockFallback(
      () => apiClient.get<PredictiveRun>(`/api/v1/predictive/${datasetId}`),
      () => mockPredictiveRun
    ),

  train: (datasetId: string, target: string) =>
    withMockFallback(
      () => apiClient.post<PredictiveRun>(`/api/v1/predictive/${datasetId}/train`, { target }),
      () => ({ ...mockPredictiveRun, target })
    ),
};
