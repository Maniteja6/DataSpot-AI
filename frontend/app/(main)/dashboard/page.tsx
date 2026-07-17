"use client";

import { Database, Sparkles, ShieldCheck, TrendingUp } from "lucide-react";
import { KpiCard } from "@/components/charts/KpiCard";
import { AreaChartCard } from "@/components/charts/AreaChartCard";
import { PieChartCard } from "@/components/charts/PieChartCard";
import { DropzoneUploader } from "@/components/upload/DropzoneUploader";
import { ExecutiveSummaryCard } from "@/components/shared/ExecutiveSummaryCard";
import { EmptyState } from "@/components/shared/EmptyState";
import { AgentActivityTimeline } from "@/features/dashboard/components/AgentActivityTimeline";
import { QuickActions } from "@/features/dashboard/components/QuickActions";
import { useDashboardData } from "@/features/dashboard/hooks/useDashboardData";
import { DashboardSkeleton } from "@/components/skeletons/DashboardSkeleton";
import { formatRelativeTime } from "@/lib/formatters";

export default function DashboardPage() {
  const {
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
    mostRecentHasData,
  } = useDashboardData();

  if (isLoading) return <DashboardSkeleton />;

  return (
    <div className="space-y-6 animate-fade-up">
      <div className="grid gap-4 md:grid-cols-4">
        <KpiCard label="Datasets processed" value={String(ready.length)} icon={Database} hint={`${totalRows.toLocaleString()} rows total`} />
        <KpiCard label="Insights generated" value={String(totalInsights)} icon={Sparkles} accent="signal" />
        <KpiCard label="Data quality score" value={`${avgQuality}%`} icon={ShieldCheck} accent="signal" hint="Across active datasets" />
        <KpiCard
          label="Best model score"
          value={bestModel ? String(bestModel.score) : "—"}
          icon={TrendingUp}
          accent="signal"
          hint={bestModel ? `${bestModel.metric} · ${bestModel.datasetName}` : "No trained models yet"}
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <div className="space-y-4 lg:col-span-2">
          {mostRecentHasData ? (
            <AreaChartCard
              title="Forecast"
              description={`${mostRecent?.name} — actual & projected`}
              data={forecastChartData}
              xKey="date"
              yKey="value"
            />
          ) : (
            <EmptyState
              icon={TrendingUp}
              title="No forecast yet"
              description={
                mostRecent
                  ? `${mostRecent.name} hasn't been analyzed yet — check back once processing completes.`
                  : "Upload a dataset to generate a forecast."
              }
            />
          )}
          <div className="glass-panel p-5">
            <p className="eyebrow mb-3">Upload dataset</p>
            <DropzoneUploader />
            {ready.length > 0 && (
              <div className="mt-4 space-y-2">
                {ready.slice(0, 3).map((d) => (
                  <div key={d.id} className="flex items-center justify-between rounded-xl border border-line px-3 py-2 text-xs">
                    <span className="text-ink">{d.name}</span>
                    <span className="text-ink-faint">{formatRelativeTime(d.uploadedAt)}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
        <div className="space-y-4">
          {insightCategoryData.length > 0 ? (
            <PieChartCard title="Insight Breakdown" description={mostRecent?.name} data={insightCategoryData} />
          ) : (
            <EmptyState
              icon={Sparkles}
              title="No insights yet"
              description={
                mostRecent
                  ? `${mostRecent.name} hasn't generated insights yet.`
                  : "Upload a dataset to generate insights."
              }
            />
          )}
          <div className="glass-panel p-5">
            <p className="eyebrow mb-3">Quick Actions</p>
            <QuickActions />
          </div>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <ExecutiveSummaryCard findings={findings} risks={risks} recommendations={recommendations} />
        </div>
        <AgentActivityTimeline datasetId={ready[0]?.id} />
      </div>
    </div>
  );
}
