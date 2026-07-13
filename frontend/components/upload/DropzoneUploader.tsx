"use client";

import { useCallback, useRef, useState } from "react";
import { UploadCloud } from "lucide-react";
import { cn } from "@/utils/cn";
import { useDatasetUpload } from "@/hooks/useDatasetUpload";
import { UploadProgress } from "./UploadProgress";

export function DropzoneUploader({ projectId }: { projectId?: string }) {
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const { items, uploadFiles } = useDatasetUpload(projectId);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      if (e.dataTransfer.files?.length) uploadFiles(e.dataTransfer.files);
    },
    [uploadFiles]
  );

  return (
    <div className="space-y-3">
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={cn(
          "flex cursor-pointer flex-col items-center justify-center gap-3 rounded-2xl border-2 border-dashed px-6 py-10 text-center transition-colors",
          isDragging ? "border-signal bg-signal-soft" : "border-line bg-bg-surface/40 hover:border-signal/40"
        )}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".csv,.xlsx,.xls"
          multiple
          hidden
          onChange={(e) => e.target.files && uploadFiles(e.target.files)}
        />
        <div className="flex h-11 w-11 items-center justify-center rounded-full bg-signal-soft">
          <UploadCloud className="h-5 w-5 text-signal" />
        </div>
        <div>
          <p className="text-sm font-medium text-ink">Drag & drop a CSV or Excel file</p>
          <p className="mt-1 text-xs text-ink-faint">or click to browse · 200MB per file · CSV, XLSX</p>
        </div>
      </div>

      {items.length > 0 && (
        <div className="space-y-2">
          {items.map((item, i) =>
            item.status === "error" ? (
              <p key={i} className="text-xs text-rose">{item.file.name} — {item.error}</p>
            ) : (
              <UploadProgress key={i} fileName={item.file.name} progress={item.progress} />
            )
          )}
        </div>
      )}
    </div>
  );
}
