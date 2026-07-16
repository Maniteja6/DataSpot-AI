"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { requirementService } from "@/services/requirement.service";
import { queryKeys } from "@/lib/react-query/queryKeys";
import type { RequirementRun } from "@/types/requirement.types";

export function useRequirementHistory(datasetId: string | null) {
  return useQuery({
    queryKey: queryKeys.requirements.byDataset(datasetId ?? "none"),
    queryFn: () => requirementService.listByDataset(datasetId as string),
    enabled: !!datasetId,
  });
}

export function useSubmitRequirement(datasetId: string | null) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (requirement: string) => requirementService.submit(datasetId as string, requirement),
    onSuccess: (run) => {
      if (!datasetId) return;
      queryClient.setQueryData<RequirementRun[]>(
        queryKeys.requirements.byDataset(datasetId),
        (old = []) => [run, ...old]
      );
    },
  });
}
