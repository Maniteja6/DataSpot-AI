"use client";

import { useDatasets } from "@/features/datasets/hooks/useDatasets";
import { useDataQuality } from "@/features/data-quality/hooks/useDataQuality";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { KpiCard } from "@/components/charts/KpiCard";
import { TableSkeleton } from "@/components/skeletons/TableSkeleton";
import { ShieldCheck, Copy, AlertTriangle, FileWarning } from "lucide-react";
import { CheckCircle2, Circle } from "lucide-react";

const SEVERITY_VARIANT = { high: "rose", medium: "amber", low: "neutral" } as const;
const TYPE_LABEL: Record<string, string> = {
  missing_values: "Missing values",
  duplicates: "Duplicates",
  outliers: "Outliers",
  schema: "Schema inconsistency",
  validation: "Validation issue",
};

export default function DataQualityPage() {
  const { data: datasets } = useDatasets();
  const datasetId = datasets?.[0]?.id ?? "ds_orders_2025";
  const { dataset, issues } = useDataQuality(datasetId);

  if (dataset.isLoading || issues.isLoading || !dataset.data) return <TableSkeleton rows={6} />;

  const d = dataset.data;
  const resolvedCount = issues.data?.filter((i) => i.resolved).length ?? 0;

  return (
    <div className="space-y-6 animate-fade-up">
      <div className="grid gap-4 md:grid-cols-4">
        <KpiCard label="Quality score" value={`${d.qualityScore}%`} icon={ShieldCheck} accent="signal" />
        <KpiCard label="Duplicate rows" value={d.duplicateRows.toLocaleString()} icon={Copy} accent="amber" />
        <KpiCard label="Missing cells" value={d.missingCells.toLocaleString()} icon={FileWarning} accent="amber" />
        <KpiCard label="Outliers flagged" value={d.outlierCount.toLocaleString()} icon={AlertTriangle} accent="rose" />
      </div>

      <Card>
        <CardHeader>
          <div>
            <CardTitle>Cleaning Pipeline</CardTitle>
            <CardDescription>{resolvedCount} of {issues.data?.length ?? 0} issues resolved automatically</CardDescription>
          </div>
        </CardHeader>
        <div className="space-y-2">
          {issues.data?.map((issue) => (
            <div key={issue.id} className="flex items-center justify-between rounded-xl border border-line p-3">
              <div className="flex items-center gap-3">
                {issue.resolved ? (
                  <CheckCircle2 className="h-4 w-4 shrink-0 text-signal" />
                ) : (
                  <Circle className="h-4 w-4 shrink-0 text-ink-faint" />
                )}
                <div>
                  <p className="text-sm text-ink">
                    {TYPE_LABEL[issue.type]}{issue.column ? ` — ${issue.column}` : ""}
                  </p>
                  <p className="text-xs text-ink-muted">{issue.suggestion}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs text-ink-faint">{issue.count.toLocaleString()}</span>
                <Badge variant={SEVERITY_VARIANT[issue.severity]}>{issue.severity}</Badge>
              </div>
            </div>
          ))}
        </div>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Column Schema</CardTitle>
          <CardDescription>Detected types and completeness</CardDescription>
        </CardHeader>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-[11px] font-mono uppercase tracking-wide text-ink-faint">
                <th className="pb-2">Column</th>
                <th className="pb-2">Type</th>
                <th className="pb-2">Missing</th>
                <th className="pb-2">Unique</th>
              </tr>
            </thead>
            <tbody>
              {d.columns.map((c) => (
                <tr key={c.name} className="border-t border-line">
                  <td className="py-2.5 text-ink">{c.name}</td>
                  <td className="py-2.5 text-ink-muted font-mono text-xs uppercase">{c.dataType}</td>
                  <td className="py-2.5 text-ink-muted">{c.missingPct}%</td>
                  <td className="py-2.5 text-ink-muted">{c.uniqueCount.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
