"use client";

import { useParams } from "next/navigation";
import { useDataQuality } from "@/features/data-quality/hooks/useDataQuality";
import { Card, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { KpiCard } from "@/components/charts/KpiCard";
import { ShieldCheck, Copy, AlertTriangle } from "lucide-react";
import { TableSkeleton } from "@/components/skeletons/TableSkeleton";

const SEVERITY_VARIANT = { high: "rose", medium: "amber", low: "neutral" } as const;

export default function DatasetQualityPage() {
  const { datasetId } = useParams<{ datasetId: string }>();
  const { dataset, issues } = useDataQuality(datasetId);

  if (dataset.isLoading || issues.isLoading || !dataset.data) return <TableSkeleton rows={6} />;
  const d = dataset.data;

  return (
    <div className="space-y-6 animate-fade-up">
      <div className="grid gap-4 md:grid-cols-3">
        <KpiCard label="Quality score" value={`${d.qualityScore}%`} icon={ShieldCheck} accent="signal" />
        <KpiCard label="Duplicates" value={d.duplicateRows.toLocaleString()} icon={Copy} accent="amber" />
        <KpiCard label="Outliers" value={d.outlierCount.toLocaleString()} icon={AlertTriangle} accent="rose" />
      </div>
      <Card>
        <CardTitle className="mb-3">Issues</CardTitle>
        <div className="space-y-2">
          {issues.data?.map((issue) => (
            <div key={issue.id} className="flex items-center justify-between rounded-xl border border-line p-3 text-sm">
              <span className="text-ink-muted">{issue.suggestion}</span>
              <Badge variant={SEVERITY_VARIANT[issue.severity]}>{issue.severity}</Badge>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
