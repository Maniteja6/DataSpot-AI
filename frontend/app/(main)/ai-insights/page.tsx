"use client";

import { useDatasets } from "@/features/datasets/hooks/useDatasets";
import { useInsights } from "@/features/data-insights/hooks/useInsights";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Card, CardTitle } from "@/components/ui/card";
import { ConfidenceBadge } from "@/components/shared/ConfidenceBadge";
import { InsightsSkeleton } from "@/components/skeletons/InsightsSkeleton";
import type { InsightCategory } from "@/types/insight.types";

const GROUPS: { key: InsightCategory | "all"; label: string }[] = [
  { key: "all", label: "All" },
  { key: "opportunity", label: "Opportunities" },
  { key: "risk", label: "Risks" },
  { key: "anomaly", label: "Anomalies" },
  { key: "trend", label: "Trends" },
  { key: "correlation", label: "Correlations" },
  { key: "prediction", label: "Predictions" },
  { key: "recommendation", label: "Recommendations" },
];

export default function AiInsightsPage() {
  const { data: datasets } = useDatasets();
  const datasetId = datasets?.[0]?.id ?? "ds_orders_2025";
  const { data: insights, isLoading } = useInsights(datasetId);

  if (isLoading || !insights) return <InsightsSkeleton />;

  return (
    <div className="animate-fade-up">
      <Tabs defaultValue="all">
        <TabsList>
          {GROUPS.map((g) => (
            <TabsTrigger key={g.key} value={g.key}>{g.label}</TabsTrigger>
          ))}
        </TabsList>

        {GROUPS.map((g) => {
          const filtered = g.key === "all" ? insights : insights.filter((i) => i.category === g.key);
          return (
            <TabsContent key={g.key} value={g.key}>
              {filtered.length === 0 ? (
                <p className="py-8 text-center text-sm text-ink-faint">No {g.label.toLowerCase()} found yet.</p>
              ) : (
                <div className="grid gap-4 md:grid-cols-2">
                  {filtered.map((insight) => (
                    <Card key={insight.id}>
                      <div className="mb-2 flex items-center justify-between">
                        <span className="font-mono text-[11px] uppercase tracking-wide text-ink-faint">
                          {insight.category.replace("_", " ")}
                        </span>
                        <ConfidenceBadge confidence={insight.confidence} />
                      </div>
                      <CardTitle className="mb-1.5 text-base">{insight.title}</CardTitle>
                      <p className="text-sm text-ink-muted">{insight.narrative}</p>
                    </Card>
                  ))}
                </div>
              )}
            </TabsContent>
          );
        })}
      </Tabs>
    </div>
  );
}
