"use client";

import { useParams } from "next/navigation";
import { useProjects } from "@/features/projects/hooks/useProjects";
import { useDatasets } from "@/features/datasets/hooks/useDatasets";
import { DropzoneUploader } from "@/components/upload/DropzoneUploader";
import { Card, CardTitle, CardDescription } from "@/components/ui/card";
import { formatBytes } from "@/utils/file-validation";
import { formatRelativeTime } from "@/lib/formatters";
import { Database } from "lucide-react";
import { TableSkeleton } from "@/components/skeletons/TableSkeleton";
import Link from "next/link";

export default function ProjectDetailPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const { data: projects, isLoading } = useProjects();
  const { data: datasets } = useDatasets();

  if (isLoading || !projects) return <TableSkeleton rows={6} />;
  const project = projects.find((p) => p.id === projectId) ?? projects[0];
  const projectDatasets = datasets?.filter((d) => d.projectId === project.id) ?? [];

  return (
    <div className="space-y-6 animate-fade-up">
      <div>
        <p className="eyebrow">Project</p>
        <h2 className="font-display text-xl font-medium text-ink">{project.name}</h2>
        <p className="mt-1 text-sm text-ink-muted">{project.description}</p>
      </div>

      <Card>
        <p className="eyebrow mb-3">Add a dataset to this project</p>
        <DropzoneUploader projectId={project.id} />
      </Card>

      <div>
        <p className="eyebrow mb-3">Datasets in this project</p>
        <div className="grid gap-4 md:grid-cols-2">
          {projectDatasets.length === 0 ? (
            <p className="text-sm text-ink-faint">No datasets uploaded yet.</p>
          ) : (
            projectDatasets.map((d) => (
              <Link key={d.id} href={`/datasets/${d.id}`}>
                <Card className="scan-hover">
                  <div className="mb-2 flex items-center gap-2">
                    <Database className="h-4 w-4 text-signal" />
                    <CardTitle className="text-sm">{d.name}</CardTitle>
                  </div>
                  <CardDescription>
                    {d.rowCount.toLocaleString()} rows · {formatBytes(d.sizeBytes)} · {formatRelativeTime(d.uploadedAt)}
                  </CardDescription>
                </Card>
              </Link>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
