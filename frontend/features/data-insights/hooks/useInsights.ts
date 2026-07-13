"use client";

import { useQuery } from "@tanstack/react-query";
import { insightsService } from "@/services/insights.service";
import { queryKeys } from "@/lib/react-query/queryKeys";

export function useInsights(datasetId: string) {
  return useQuery({
    queryKey: queryKeys.insights.byDataset(datasetId),
    queryFn: () => insightsService.listByDataset(datasetId),
  });
}

export function useCorrelations(datasetId: string) {
  return useQuery({
    queryKey: [...queryKeys.insights.byDataset(datasetId), "correlations"],
    queryFn: () => insightsService.correlations(datasetId),
  });
}

export function useColumnProfiles(datasetId: string) {
  return useQuery({
    queryKey: [...queryKeys.insights.byDataset(datasetId), "columns"],
    queryFn: () => insightsService.columnProfiles(datasetId),
  });
}
