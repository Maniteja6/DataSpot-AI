"use client";

import { Database, Sparkles, ShieldCheck, TrendingUp } from "lucide-react";
import { KpiCard } from "@/components/charts/KpiCard";
import { AreaChartCard } from "@/components/charts/AreaChartCard";
import { PieChartCard } from "@/components/charts/PieChartCard";
import { DropzoneUploader } from "@/components/upload/DropzoneUploader";
import { ExecutiveSummaryCard } from "@/components/shared/ExecutiveSummaryCard";
import { AgentActivityTimeline } from "@/features/dashboard/components/AgentActivityTimeline";
import { QuickActions } from "@/features/dashboard/components/QuickActions";
import { useDatasets } from "@/features/datasets/hooks/useDatasets";
import { DashboardSkeleton } from "@/components/skeletons/DashboardSkeleton";
import { formatRelativeTime } from "@/lib/formatters";

const revenueTrend = [
  { month: "Jul", revenue: 38200 },
  { month: "Aug", revenue: 40100 },
  { month: "Sep", revenue: 39800 },
  { month: "Oct", revenue: 43500 },
  { month: "Nov", revenue: 47200 },
  { month: "Dec", revenue: 49800 },
];

const regionSplit = [
  { name: "West", value: 42 },
  { name: "East", value: 26 },
  { name: "Midwest", value: 18 },
  { name: "South", value: 14 },
];

export default function DashboardPage() {
  const { data: datasets, isLoading } = useDatasets();

  if (isLoading) return <DashboardSkeleton />;

  const ready = datasets ?? [];
  const totalRows = ready.reduce((sum, d) => sum + d.rowCount, 0);
  const avgQuality = ready.length
    ? Math.round(ready.reduce((sum, d) => sum + d.qualityScore, 0) / ready.length)
    : 0;

  return (
    <div className="space-y-6 animate-fade-up">
      <div className="grid gap-4 md:grid-cols-4">
        <KpiCard label="Datasets processed" value={String(ready.length)} icon={Database} hint={`${totalRows.toLocaleString()} rows total`} />
        <KpiCard label="Insights generated" value="47" icon={Sparkles} delta={12} accent="signal" />
        <KpiCard label="Data quality score" value={`${avgQuality}%`} icon={ShieldCheck} accent="signal" hint="Across active datasets" />
        <KpiCard label="Forecast accuracy" value="91.9%" icon={TrendingUp} delta={3} accent="signal" hint="MAPE 8.1%" />
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <div className="space-y-4 lg:col-span-2">
          <AreaChartCard title="Revenue Trend" description="Last 6 months, all regions" data={revenueTrend} xKey="month" yKey="revenue" />
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
          <PieChartCard title="Revenue by Region" data={regionSplit} />
          <div className="glass-panel p-5">
            <p className="eyebrow mb-3">Quick Actions</p>
            <QuickActions />
          </div>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <ExecutiveSummaryCard
            findings={[
              "Revenue trending up ~$900/month with West region leading growth.",
              "Order volume anomaly detected on Nov 14 in the Midwest region.",
              "Bundled SKUs carry 18% higher margin than single-item orders.",
            ]}
            risks={[
              "Customers with declining order frequency churn at 3.4x baseline.",
              "1,032 missing cells detected in orders_q4_2025.csv before cleaning.",
            ]}
            recommendations={[
              "Shift 15% of Midwest ad spend toward West region bundles.",
              "Launch an automated win-back flow for at-risk customers.",
            ]}
          />
        </div>
        <AgentActivityTimeline />
      </div>
    </div>
  );
}
