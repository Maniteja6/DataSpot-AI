"use client";

import { cn } from "@/utils/cn";

export function UploadProgress({ fileName, progress }: { fileName: string; progress: number }) {
  return (
    <div className="rounded-xl border border-line bg-bg-surface/60 p-3">
      <div className="mb-2 flex items-center justify-between text-xs">
        <span className="truncate text-ink">{fileName}</span>
        <span className="font-mono text-ink-faint">{progress}%</span>
      </div>
      <div className="h-1.5 w-full overflow-hidden rounded-full bg-bg-raised">
        <div
          className={cn("h-full rounded-full bg-signal transition-all duration-200")}
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  );
}
