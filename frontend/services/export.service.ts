import { apiClient, withMockFallback } from "./api-client";

export type ExportFormat = "pdf" | "excel" | "csv" | "json" | "pptx";

export interface ExportJob {
  id: string;
  format: ExportFormat;
  label: string;
  status: "queued" | "processing" | "ready" | "error";
  downloadUrl?: string;
  createdAt: string;
}

export const exportService = {
  requestExport: (datasetId: string, format: ExportFormat) =>
    withMockFallback(
      () => apiClient.post<ExportJob>(`/api/v1/export`, { datasetId, format }),
      () => ({
        id: `exp_${Date.now()}`,
        format,
        label: `${format.toUpperCase()} export`,
        status: "ready" as const,
        downloadUrl: "#",
        createdAt: new Date().toISOString(),
      })
    ),
};
