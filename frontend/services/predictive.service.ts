import { apiClient, withMockFallback, ApiClientError } from "./api-client";
import { mockPredictiveRun } from "./mocks/mockData";
import type { PredictiveRun } from "@/types/prediction.types";

export const predictiveService = {
  getRun: (datasetId: string) =>
    withMockFallback(
      () => apiClient.get<PredictiveRun>(`/api/v1/predictive/${datasetId}`),
      () => mockPredictiveRun
    ),

  /**
   * Bypasses the mock fallback — a 404 here means "no run yet" and must
   * surface as null, not silently become fake forecast data. Used by
   * dashboard aggregation, where showing real zeros/empty-states matters
   * more than graceful degradation.
   */
  getRunSafe: async (datasetId: string): Promise<PredictiveRun | null> => {
    try {
      return await apiClient.get<PredictiveRun>(`/api/v1/predictive/${datasetId}`);
    } catch (err) {
      if (err instanceof ApiClientError && err.status === 404) return null;
      throw err;
    }
  },

  train: (datasetId: string, target: string) =>
    withMockFallback(
      () => apiClient.post<PredictiveRun>(`/api/v1/predictive/${datasetId}/train`, { target }),
      () => ({ ...mockPredictiveRun, target })
    ),
};
