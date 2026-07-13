"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { predictiveService } from "@/services/predictive.service";
import { queryKeys } from "@/lib/react-query/queryKeys";

export function usePredictiveRun(datasetId: string) {
  return useQuery({
    queryKey: queryKeys.predictive.byDataset(datasetId),
    queryFn: () => predictiveService.getRun(datasetId),
  });
}

export function useTrainModel(datasetId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (target: string) => predictiveService.train(datasetId, target),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: queryKeys.predictive.byDataset(datasetId) }),
  });
}
