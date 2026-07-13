"use client";

import { useParams } from "next/navigation";
import { usePredictiveRun } from "@/features/predictive-analysis/hooks/usePredictiveRun";
import { ForecastChart } from "@/components/charts/ForecastChart";
import { BarChartCard } from "@/components/charts/BarChartCard";
import { Card, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TableSkeleton } from "@/components/skeletons/TableSkeleton";

export default function DatasetPredictivePage() {
  const { datasetId } = useParams<{ datasetId: string }>();
  const { data: run, isLoading } = usePredictiveRun(datasetId);

  if (isLoading || !run) return <TableSkeleton rows={6} />;

  return (
    <div className="space-y-6 animate-fade-up">
      <Card>
        <CardTitle className="mb-3">Model Candidates</CardTitle>
        <div className="space-y-2">
          {run.candidates.map((c) => (
            <div key={c.id} className="flex items-center justify-between rounded-lg border border-line px-3 py-2 text-sm">
              <span className="text-ink">{c.name}</span>
              <div className="flex items-center gap-2">
                <span className="text-ink-muted">{c.metric} {c.score.toFixed(3)}</span>
                {c.isBest && <Badge variant="signal">Best</Badge>}
              </div>
            </div>
          ))}
        </div>
      </Card>
      <ForecastChart data={run.forecast} />
      <BarChartCard
        title="Feature Importance"
        data={run.featureImportance.map((f) => ({ feature: f.feature, importance: Math.round(f.importance * 100) }))}
        xKey="feature"
        yKey="importance"
      />
    </div>
  );
}
