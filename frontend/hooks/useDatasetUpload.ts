"use client";

import { useState, useCallback } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { datasetsService } from "@/services/datasets.service";
import { useDatasetStore } from "@/stores/useDatasetStore";
import { validateDatasetFile } from "@/utils/file-validation";
import { queryKeys } from "@/lib/react-query/queryKeys";

export interface UploadItem {
  file: File;
  progress: number;
  status: "uploading" | "done" | "error";
  error?: string;
}

export function useDatasetUpload(projectId?: string) {
  const [items, setItems] = useState<UploadItem[]>([]);
  const upsertDataset = useDatasetStore((s) => s.upsertDataset);
  const queryClient = useQueryClient();

  const uploadFiles = useCallback(
    async (files: FileList | File[]) => {
      const fileArray = Array.from(files);

      for (const file of fileArray) {
        const validation = validateDatasetFile(file);
        if (!validation.valid) {
          setItems((prev) => [...prev, { file, progress: 0, status: "error", error: validation.error }]);
          continue;
        }

        setItems((prev) => [...prev, { file, progress: 0, status: "uploading" }]);

        try {
          const dataset = await datasetsService.upload(file, projectId, (pct) => {
            setItems((prev) =>
              prev.map((it) => (it.file === file ? { ...it, progress: pct } : it))
            );
          });
          upsertDataset(dataset);
          setItems((prev) =>
            prev.map((it) => (it.file === file ? { ...it, progress: 100, status: "done" } : it))
          );
          queryClient.invalidateQueries({ queryKey: queryKeys.datasets.all });
        } catch (err) {
          setItems((prev) =>
            prev.map((it) =>
              it.file === file
                ? { ...it, status: "error", error: "Upload failed. Try again." }
                : it
            )
          );
        }
      }
    },
    [projectId, upsertDataset, queryClient]
  );

  return { items, uploadFiles, clear: () => setItems([]) };
}
