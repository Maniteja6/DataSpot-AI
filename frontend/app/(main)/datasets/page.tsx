"use client";

import Link from "next/link";
import { useDatasets } from "@/features/datasets/hooks/useDatasets";
import { DropzoneUploader } from "@/components/upload/DropzoneUploader";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatBytes } from "@/utils/file-validation";
import { formatRelativeTime } from "@/lib/formatters";
import { Database } from "lucide-react";
import { EmptyState } from "@/components/shared/EmptyState";
import { TableSkeleton } from "@/components/skeletons/TableSkeleton";

const STATUS_VARIANT = { ready: "signal", processing: "amber", uploading: "amber", error: "rose" } as const;

export default function DatasetsPage() {
  const { data: datasets, isLoading } = useDatasets();

  return (
    <div className="space-y-6 animate-fade-up">
      <Card>
        <p className="eyebrow mb-3">Upload a new dataset</p>
        <DropzoneUploader />
      </Card>

      {isLoading ? (
        <TableSkeleton rows={4} />
      ) : !datasets || datasets.length === 0 ? (
        <EmptyState icon={Database} title="No datasets yet" description="Drag a CSV or Excel file above to kick off the full AI pipeline." />
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {datasets.map((d) => (
            <Link key={d.id} href={`/datasets/${d.id}`}>
              <Card className="scan-hover flex items-start justify-between">
                <div>
                  <div className="mb-2 flex items-center gap-2">
                    <Database className="h-4 w-4 text-signal" />
                    <p className="font-medium text-ink">{d.name}</p>
                  </div>
                  <p className="text-xs text-ink-muted">
                    {d.rowCount.toLocaleString()} rows · {d.columnCount} columns · {formatBytes(d.sizeBytes)}
                  </p>
                  <p className="mt-1 text-xs text-ink-faint">Uploaded {formatRelativeTime(d.uploadedAt)}</p>
                </div>
                <Badge variant={STATUS_VARIANT[d.status]}>{d.status}</Badge>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
