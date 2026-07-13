"use client";

import { useParams } from "next/navigation";
import { useDataset } from "@/features/datasets/hooks/useDatasets";
import { usePipelineStatus } from "@/hooks/usePipelineStatus";
import { Card, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { KpiCard } from "@/components/charts/KpiCard";
import { AgentStatusPill } from "@/components/shared/AgentStatusPill";
import { formatBytes } from "@/utils/file-validation";
import { formatRelativeTime } from "@/lib/formatters";
import { Rows3, Columns3, ShieldCheck, HardDrive } from "lucide-react";
import { TableSkeleton } from "@/components/skeletons/TableSkeleton";
import Link from "next/link";

export default function DatasetDetailPage() {
  const { datasetId } = useParams<{ datasetId: string }>();
  const { data: dataset, isLoading } = useDataset(datasetId);
  const { data: pipeline } = usePipelineStatus(datasetId);

  if (isLoading || !dataset) return <TableSkeleton rows={8} />;

  return (
    <div className="space-y-6 animate-fade-up">
      <div className="flex items-center justify-between">
        <div>
          <p className="eyebrow">Dataset</p>
          <h2 className="font-display text-xl font-medium text-ink">{dataset.name}</h2>
        </div>
        <Badge variant="signal">{dataset.status}</Badge>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <KpiCard label="Rows" value={dataset.rowCount.toLocaleString()} icon={Rows3} />
        <KpiCard label="Columns" value={String(dataset.columnCount)} icon={Columns3} />
        <KpiCard label="Quality score" value={`${dataset.qualityScore}%`} icon={ShieldCheck} accent="signal" />
        <KpiCard label="File size" value={formatBytes(dataset.sizeBytes)} icon={HardDrive} />
      </div>

      <Card>
        <CardTitle className="mb-4">Pipeline progress</CardTitle>
        <div className="space-y-3">
          {pipeline?.stages.map((stage) => (
            <div key={stage.key}>
              <div className="mb-1 flex items-center justify-between text-xs">
                <span className="text-ink-muted">{stage.label}</span>
                <AgentStatusPill status={stage.status} />
              </div>
              <div className="h-1.5 w-full overflow-hidden rounded-full bg-bg-raised">
                <div className="h-full rounded-full bg-signal transition-all" style={{ width: `${stage.progress}%` }} />
              </div>
            </div>
          ))}
        </div>
      </Card>

      <div className="grid gap-4 md:grid-cols-3">
        <Link href="/data-insights"><Card className="scan-hover"><CardTitle className="text-sm">View Insights</CardTitle><CardDescription>Distributions, correlations, trends</CardDescription></Card></Link>
        <Link href="/predictive-analysis"><Card className="scan-hover"><CardTitle className="text-sm">Run Forecast</CardTitle><CardDescription>Model comparison and predictions</CardDescription></Card></Link>
        <Link href="/decision-making"><Card className="scan-hover"><CardTitle className="text-sm">Decisions</CardTitle><CardDescription>Strategic recommendations</CardDescription></Card></Link>
      </div>

      <Card>
        <CardTitle className="mb-3">Schema</CardTitle>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-[11px] font-mono uppercase tracking-wide text-ink-faint">
                <th className="pb-2">Column</th>
                <th className="pb-2">Type</th>
                <th className="pb-2">Missing %</th>
                <th className="pb-2">Unique</th>
                <th className="pb-2">Sample</th>
              </tr>
            </thead>
            <tbody>
              {dataset.columns.map((c) => (
                <tr key={c.name} className="border-t border-line">
                  <td className="py-2.5 text-ink">{c.name}</td>
                  <td className="py-2.5 font-mono text-xs uppercase text-ink-muted">{c.dataType}</td>
                  <td className="py-2.5 text-ink-muted">{c.missingPct}%</td>
                  <td className="py-2.5 text-ink-muted">{c.uniqueCount.toLocaleString()}</td>
                  <td className="py-2.5 text-ink-faint">{c.sampleValues.join(", ")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="mt-3 text-xs text-ink-faint">Uploaded {formatRelativeTime(dataset.uploadedAt)}</p>
      </Card>
    </div>
  );
}
