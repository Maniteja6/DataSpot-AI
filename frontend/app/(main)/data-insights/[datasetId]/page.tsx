"use client";

import { useParams } from "next/navigation";
import { useInsights, useCorrelations, useColumnProfiles } from "@/features/data-insights/hooks/useInsights";
import { BarChartCard } from "@/components/charts/BarChartCard";
import { CorrelationHeatmap } from "@/components/charts/CorrelationHeatmap";
import { Card, CardTitle } from "@/components/ui/card";
import { ConfidenceBadge } from "@/components/shared/ConfidenceBadge";
import { Badge } from "@/components/ui/badge";
import { InsightsSkeleton } from "@/components/skeletons/InsightsSkeleton";

export default function DatasetInsightsPage() {
  const { datasetId } = useParams<{ datasetId: string }>();
  const { data: insights, isLoading } = useInsights(datasetId);
  const { data: correlations } = useCorrelations(datasetId);
  const { data: columnProfiles } = useColumnProfiles(datasetId);

  if (isLoading || !insights) return <InsightsSkeleton />;

  return (
    <div className="space-y-6 animate-fade-up">
      <div className="grid gap-4 md:grid-cols-2">
        {insights.map((insight) => (
          <Card key={insight.id}>
            <div className="mb-2 flex items-center justify-between">
              <Badge variant="neutral">{insight.category.replace("_", " ")}</Badge>
              <ConfidenceBadge confidence={insight.confidence} />
            </div>
            <CardTitle className="mb-1.5 text-base">{insight.title}</CardTitle>
            <p className="text-sm text-ink-muted">{insight.narrative}</p>
          </Card>
        ))}
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        {columnProfiles?.map((p) => (
          <BarChartCard key={p.column} title={`Distribution — ${p.column}`} data={p.histogram} xKey="bucket" yKey="count" multiColor />
        ))}
      </div>
      {correlations && <CorrelationHeatmap pairs={correlations} />}
    </div>
  );
}
