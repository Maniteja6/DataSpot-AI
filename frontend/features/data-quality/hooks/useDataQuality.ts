"use client";

import { useQuery } from "@tanstack/react-query";
import { dataQualityService } from "@/services/data-quality.service";

export function useDataQuality(datasetId: string) {
  const dataset = useQuery({
    queryKey: ["data-quality", datasetId],
    queryFn: () => dataQualityService.getDataset(datasetId),
  });
  const issues = useQuery({
    queryKey: ["data-quality", datasetId, "issues"],
    queryFn: () => dataQualityService.getIssues(datasetId),
  });
  return { dataset, issues };
}
