"use client";

import { useDatasets } from "@/features/datasets/hooks/useDatasets";
import { useInsights, useCorrelations, useColumnProfiles } from "@/features/data-insights/hooks/useInsights";
import { BarChartCard } from "@/components/charts/BarChartCard";
import { ScatterPlot } from "@/components/charts/ScatterPlot";
import { CorrelationHeatmap } from "@/components/charts/CorrelationHeatmap";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { ConfidenceBadge } from "@/components/shared/ConfidenceBadge";
import { Badge } from "@/components/ui/badge";
import { InsightsSkeleton } from "@/components/skeletons/InsightsSkeleton";
import { EmptyState } from "@/components/shared/EmptyState";
import { Sparkles } from "lucide-react";

const CATEGORY_VARIANT = {
  opportunity: "signal",
  risk: "rose",
  anomaly: "amber",
  trend: "signal",
  correlation: "neutral",
  prediction: "signal",
  recommendation: "amber",
  executive_observation: "neutral",
} as const;

function scatterFromHistogram(histogram: { bucket: string; count: number }[]) {
  return histogram.map((h, i) => ({ x: i, y: h.count, z: h.count }));
}

export default function DataInsightsPage() {
  const { data: datasets } = useDatasets();
  const datasetId = datasets?.[0]?.id ?? null;

  const { data: insights, isLoading } = useInsights(datasetId ?? "");
  const { data: correlations } = useCorrelations(datasetId ?? "");
  const { data: columnProfiles } = useColumnProfiles(datasetId ?? "");

  if (datasetId && isLoading) return <InsightsSkeleton />;

  if (!datasetId || !insights || insights.length === 0) {
    return (
      <EmptyState
        icon={Sparkles}
        title="No insights yet"
        description="Upload a dataset from the Dashboard to generate column profiling, correlations, and narrative insights."
      />
    );
  }

  return (
    <div className="space-y-6 animate-fade-up">
      <div className="grid gap-4 md:grid-cols-2">
        {insights.map((insight) => (
          <Card key={insight.id}>
            <div className="mb-2 flex items-center justify-between">
              <Badge variant={CATEGORY_VARIANT[insight.category]}>{insight.category.replace("_", " ")}</Badge>
              <ConfidenceBadge confidence={insight.confidence} />
            </div>
            <CardTitle className="mb-1.5 text-base">{insight.title}</CardTitle>
            <p className="text-sm text-ink-muted">{insight.narrative}</p>
            <div className="mt-3 flex flex-wrap gap-1.5">
              {insight.relatedColumns.map((c) => (
                <span key={c} className="rounded-full bg-bg-raised px-2 py-0.5 font-mono text-[10px] text-ink-faint">
                  {c}
                </span>
              ))}
            </div>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        {columnProfiles?.map((profile) => (
          <BarChartCard
            key={profile.column}
            title={`Distribution — ${profile.column}`}
            description={`Mean ${profile.mean?.toFixed(1)} · Median ${profile.median} · σ ${profile.stdDev?.toFixed(1)}`}
            data={profile.histogram}
            xKey="bucket"
            yKey="count"
            multiColor
          />
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        {columnProfiles?.[0] && (
          <ScatterPlot
            title="Revenue vs. Units (sampled)"
            description="Point size reflects order count in bucket"
            data={scatterFromHistogram(columnProfiles[0].histogram)}
            xLabel="Bucket index"
            yLabel="Count"
          />
        )}
        {correlations && <CorrelationHeatmap pairs={correlations} />}
      </div>
    </div>
  );
}
