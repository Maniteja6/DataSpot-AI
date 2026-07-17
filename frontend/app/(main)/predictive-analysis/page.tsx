"use client";

import { useState } from "react";
import { useDatasets } from "@/features/datasets/hooks/useDatasets";
import { usePredictiveRun, useTrainModel } from "@/features/predictive-analysis/hooks/usePredictiveRun";
import { ForecastChart } from "@/components/charts/ForecastChart";
import { BarChartCard } from "@/components/charts/BarChartCard";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { TableSkeleton } from "@/components/skeletons/TableSkeleton";
import { EmptyState } from "@/components/shared/EmptyState";
import { Sparkles, TrendingUp } from "lucide-react";

export default function PredictiveAnalysisPage() {
  const { data: datasets } = useDatasets();
  const datasetId = datasets?.[0]?.id ?? null;
  const { data: run, isLoading } = usePredictiveRun(datasetId ?? "");
  const trainModel = useTrainModel(datasetId ?? "");
  const [target, setTarget] = useState("revenue");

  if (!datasetId) {
    return (
      <EmptyState
        icon={TrendingUp}
        title="No dataset yet"
        description="Upload a dataset from the Dashboard to train predictive models and generate forecasts."
      />
    );
  }

  if (isLoading || !run) return <TableSkeleton rows={8} />;

  return (
    <div className="space-y-6 animate-fade-up">
      <Card>
        <CardHeader>
          <div>
            <CardTitle>Model Training</CardTitle>
            <CardDescription>Target: {run.target} · Task: {run.task}</CardDescription>
          </div>
          <Button size="sm" onClick={() => trainModel.mutate(target)} disabled={trainModel.isPending}>
            <Sparkles className="h-3.5 w-3.5" /> {trainModel.isPending ? "Training…" : "Retrain"}
          </Button>
        </CardHeader>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-[11px] font-mono uppercase tracking-wide text-ink-faint">
                <th className="pb-2">Model</th>
                <th className="pb-2">Metric</th>
                <th className="pb-2">Score</th>
                <th className="pb-2">Train time</th>
                <th className="pb-2" />
              </tr>
            </thead>
            <tbody>
              {run.candidates.map((c) => (
                <tr key={c.id} className="border-t border-line">
                  <td className="py-2.5 text-ink">{c.name}</td>
                  <td className="py-2.5 text-ink-muted">{c.metric}</td>
                  <td className="py-2.5 text-ink-muted">{c.score.toFixed(3)}</td>
                  <td className="py-2.5 text-ink-muted">{c.trainingTimeSeconds}s</td>
                  <td className="py-2.5">{c.isBest && <Badge variant="signal">Best</Badge>}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      <ForecastChart data={run.forecast} />

      <div className="grid gap-4 lg:grid-cols-2">
        <BarChartCard
          title="Feature Importance"
          description="Relative contribution to model predictions"
          data={run.featureImportance.map((f) => ({ feature: f.feature, importance: Math.round(f.importance * 100) }))}
          xKey="feature"
          yKey="importance"
        />
        <Card>
          <CardHeader>
            <CardTitle>Model Reasoning</CardTitle>
          </CardHeader>
          <p className="text-sm text-ink-muted">{run.explanation}</p>
        </Card>
      </div>
    </div>
  );
}
