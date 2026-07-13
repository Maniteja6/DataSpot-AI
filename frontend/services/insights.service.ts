import { apiClient, withMockFallback } from "./api-client";
import { mockInsights, mockCorrelations, mockColumnProfiles } from "./mocks/mockData";
import type { Insight, CorrelationPair, ColumnProfile } from "@/types/insight.types";

export const insightsService = {
  listByDataset: (datasetId: string) =>
    withMockFallback(
      () => apiClient.get<Insight[]>(`/api/v1/insights?datasetId=${datasetId}`),
      () => mockInsights.filter((i) => i.datasetId === datasetId || true)
    ),

  correlations: (datasetId: string) =>
    withMockFallback(
      () => apiClient.get<CorrelationPair[]>(`/api/v1/insights/${datasetId}/correlations`),
      () => mockCorrelations
    ),

  columnProfiles: (datasetId: string) =>
    withMockFallback(
      () => apiClient.get<ColumnProfile[]>(`/api/v1/insights/${datasetId}/columns`),
      () => mockColumnProfiles
    ),
};
