"use client";

import { useQuery } from "@tanstack/react-query";
import { datasetsService } from "@/services/datasets.service";
import { queryKeys } from "@/lib/react-query/queryKeys";

export function useDatasets() {
  return useQuery({ queryKey: queryKeys.datasets.all, queryFn: datasetsService.list });
}

export function useDataset(id: string | null) {
  return useQuery({
    queryKey: queryKeys.datasets.detail(id ?? "none"),
    queryFn: () => datasetsService.get(id as string),
    enabled: !!id,
  });
}
