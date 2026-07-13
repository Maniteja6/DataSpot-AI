"use client";

import { useMutation } from "@tanstack/react-query";
import { exportService, type ExportFormat } from "@/services/export.service";

export function useExport(datasetId: string) {
  return useMutation({
    mutationFn: (format: ExportFormat) => exportService.requestExport(datasetId, format),
  });
}
