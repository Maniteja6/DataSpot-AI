"use client";

import { useQueries } from "@tanstack/react-query";
import { useDatasets } from "@/features/datasets/hooks/useDatasets";
import { useDecisions } from "@/features/decision-making/hooks/useDecisions";
import { insightsService } from "@/services/insights.service";
import { predictiveService } from "@/services/predictive.service";
import { queryKeys } from "@/lib/react-query/queryKeys";
import type { Insight, InsightCategory } from "@/types/insight.types";
import type { PredictiveRun } from "@/types/prediction.types";

const FINDING_CATEGORIES: InsightCategory[] = ["trend", "correlation", "opportunity", "executive_observation"];
const RISK_CATEGORIES: InsightCategory[] = ["risk", "anomaly"];
const MAX_LIST_ITEMS = 4;

export function useDashboardData() {
  const { data: datasets, isLoading: datasetsLoading } = useDatasets();
  const ready = (datasets ?? []).filter((d) => d.status === "ready");
  const mostRecent = ready[0] ?? null;

  const insightQueries = useQueries({
    queries: ready.map((d) => ({
      queryKey: queryKeys.insights.byDataset(d.id),
      queryFn: () => insightsService.listByDataset(d.id),
    })),
  });

  const predictiveQueries = useQueries({
    queries: ready.map((d) => ({
      queryKey: queryKeys.predictive.byDataset(d.id),
      queryFn: () => predictiveService.getRunSafe(d.id),
    })),
  });

  const { data: recentDecisions } = useDecisions(mostRecent?.id ?? "");

  const isLoading =
    datasetsLoading || insightQueries.some((q) => q.isLoading) || predictiveQueries.some((q) => q.isLoading);

  const allInsights: Insight[] = insightQueries.flatMap((q) => q.data ?? []);
  const totalInsights = allInsights.length;

  const avgQuality = ready.length
    ? Math.round(ready.reduce((sum, d) => sum + d.qualityScore, 0) / ready.length)
    : 0;
  const totalRows = ready.reduce((sum, d) => sum + d.rowCount, 0);

  const runs: (PredictiveRun | null)[] = predictiveQueries.map((q) => q.data ?? null);
  const bestModel = runs.reduce<{ score: number; metric: string; datasetName: string } | null>(
    (best, run, i) => {
      if (!run) return best;
      const top = run.candidates.find((c) => c.isBest) ?? run.candidates[0];
      if (!top) return best;
      if (!best) return { score: top.score, metric: top.metric, datasetName: ready[i].name };
      return best;
    },
    null
  );

  const mostRecentIndex = mostRecent ? ready.findIndex((d) => d.id === mostRecent.id) : -1;
  const mostRecentInsights = mostRecentIndex >= 0 ? insightQueries[mostRecentIndex]?.data ?? [] : [];
  const mostRecentRun = mostRecentIndex >= 0 ? predictiveQueries[mostRecentIndex]?.data ?? null : null;

  const forecastChartData = (mostRecentRun?.forecast ?? [])
    .map((p) => ({ date: p.date, value: p.actual ?? p.forecast ?? null }))
    .filter((p): p is { date: string; value: number } => p.value !== null);

  const categoryCounts = new Map<string, number>();
  for (const insight of mostRecentInsights) {
    categoryCounts.set(insight.category, (categoryCounts.get(insight.category) ?? 0) + 1);
  }
  const insightCategoryData = Array.from(categoryCounts.entries()).map(([name, value]) => ({ name, value }));

  const findings = mostRecentInsights
    .filter((i) => FINDING_CATEGORIES.includes(i.category))
    .slice(0, MAX_LIST_ITEMS)
    .map((i) => i.title);
  const risks = mostRecentInsights
    .filter((i) => RISK_CATEGORIES.includes(i.category))
    .slice(0, MAX_LIST_ITEMS)
    .map((i) => i.title);
  const recommendations = [...(recentDecisions ?? [])]
    .sort((a, b) => b.expectedRoiPct - a.expectedRoiPct)
    .slice(0, MAX_LIST_ITEMS)
    .map((d) => d.title);

  return {
    isLoading,
    ready,
    mostRecent,
    totalRows,
    totalInsights,
    avgQuality,
    bestModel,
    forecastChartData,
    insightCategoryData,
    findings,
    risks,
    recommendations,
    mostRecentHasData: mostRecentInsights.length > 0 || !!mostRecentRun,
  };
}
