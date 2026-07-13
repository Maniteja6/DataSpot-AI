import { apiClient, withMockFallback } from "./api-client";
import { mockDecisions } from "./mocks/mockData";
import type { DecisionCard, ScenarioAssumption } from "@/types/decision.types";

export const decisionService = {
  listByDataset: (datasetId: string) =>
    withMockFallback(
      () => apiClient.get<DecisionCard[]>(`/api/v1/decisions?datasetId=${datasetId}`),
      () => mockDecisions
    ),

  updateStatus: (id: string, status: DecisionCard["status"]) =>
    withMockFallback(
      () => apiClient.put<DecisionCard>(`/api/v1/decisions/${id}`, { status }),
      () => ({ ...mockDecisions.find((d) => d.id === id)!, status })
    ),

  runScenario: (id: string, assumptions: ScenarioAssumption[]) =>
    withMockFallback(
      () => apiClient.post<{ projectedValue: number }>(`/api/v1/decisions/${id}/scenario`, { assumptions }),
      () => {
        const base = mockDecisions.find((d) => d.id === id)?.estimatedValue ?? 100000;
        const multiplier = assumptions.reduce((acc, a) => acc * (1 + (a.value - a.min) / (a.max - a.min || 1) * 0.3), 1);
        return { projectedValue: Math.round(base * multiplier) };
      }
    ),
};
