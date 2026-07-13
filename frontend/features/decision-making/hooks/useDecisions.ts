"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { decisionService } from "@/services/decision.service";
import { queryKeys } from "@/lib/react-query/queryKeys";
import type { DecisionCard, ScenarioAssumption } from "@/types/decision.types";

export function useDecisions(datasetId: string) {
  return useQuery({
    queryKey: queryKeys.decisions.byDataset(datasetId),
    queryFn: () => decisionService.listByDataset(datasetId),
  });
}

export function useUpdateDecisionStatus(datasetId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: DecisionCard["status"] }) =>
      decisionService.updateStatus(id, status),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: queryKeys.decisions.byDataset(datasetId) }),
  });
}

export function useRunScenario(id: string) {
  return useMutation({
    mutationFn: (assumptions: ScenarioAssumption[]) => decisionService.runScenario(id, assumptions),
  });
}
