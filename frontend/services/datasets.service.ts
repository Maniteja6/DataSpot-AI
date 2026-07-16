import { apiClient, withMockFallback } from "./api-client";
import { mockDatasets } from "./mocks/mockData";
import { getSessionId } from "@/lib/session";
import type { Dataset } from "@/types/dataset.types";

export const datasetsService = {
  list: () =>
    withMockFallback(
      () => apiClient.get<Dataset[]>(`/api/v1/datasets?projectId=${getSessionId()}`),
      () => mockDatasets
    ),

  get: (id: string) =>
    withMockFallback(
      () => apiClient.get<Dataset>(`/api/v1/datasets/${id}`),
      () => mockDatasets.find((d) => d.id === id) ?? mockDatasets[0]
    ),

  upload: (file: File, projectId?: string, onProgress?: (pct: number) => void) =>
    withMockFallback(
      async () => {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("projectId", projectId ?? getSessionId());
        return apiClient.post<Dataset>("/api/v1/datasets/upload", formData);
      },
      () =>
        new Promise<Dataset>((resolve) => {
          let pct = 0;
          const interval = setInterval(() => {
            pct = Math.min(100, pct + Math.random() * 22);
            onProgress?.(Math.round(pct));
            if (pct >= 100) {
              clearInterval(interval);
              resolve({
                ...mockDatasets[0],
                id: `ds_${Date.now()}`,
                name: file.name,
                sizeBytes: file.size,
                status: "processing",
                uploadedAt: new Date().toISOString(),
              });
            }
          }, 220);
        })
    ),

  remove: (id: string) =>
    withMockFallback(
      () => apiClient.delete<{ success: boolean }>(`/api/v1/datasets/${id}`),
      () => ({ success: true })
    ),
};
