"use client";

import { useParams } from "next/navigation";
import { useDatasets } from "@/features/datasets/hooks/useDatasets";
import { useDecisions } from "@/features/decision-making/hooks/useDecisions";
import { WhatIfSimulator } from "@/features/decision-making/components/WhatIfSimulator";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ConfidenceBadge } from "@/components/shared/ConfidenceBadge";
import { formatCurrency } from "@/lib/formatters";
import { InsightsSkeleton } from "@/components/skeletons/InsightsSkeleton";

export default function ScenarioPage() {
  const { id } = useParams<{ id: string }>();
  const { data: datasets } = useDatasets();
  const datasetId = datasets?.[0]?.id ?? "ds_orders_2025";
  const { data: decisions, isLoading } = useDecisions(datasetId);

  if (isLoading || !decisions) return <InsightsSkeleton />;
  const decision = decisions.find((d) => d.id === id) ?? decisions[0];

  return (
    <div className="grid gap-6 lg:grid-cols-2 animate-fade-up">
      <Card>
        <CardHeader>
          <div>
            <CardTitle>{decision.title}</CardTitle>
            <CardDescription>Scenario analysis</CardDescription>
          </div>
          <ConfidenceBadge confidence={decision.confidence} />
        </CardHeader>
        <p className="text-sm text-ink-muted">{decision.narrative}</p>
        <div className="mt-4 flex flex-wrap gap-2">
          <Badge variant="neutral">{decision.area}</Badge>
          <Badge variant="signal">{decision.expectedRoiPct}% baseline ROI</Badge>
          <Badge variant="neutral">{formatCurrency(decision.estimatedValue)} baseline value</Badge>
        </div>
        <div className="mt-5">
          <p className="eyebrow mb-2">Recommended next steps</p>
          <ol className="space-y-2">
            {decision.actionSteps.map((step, i) => (
              <li key={i} className="flex gap-2 text-sm text-ink-muted">
                <span className="font-mono text-signal">{String(i + 1).padStart(2, "0")}</span>
                {step}
              </li>
            ))}
          </ol>
        </div>
      </Card>

      <WhatIfSimulator decisionId={decision.id} />
    </div>
  );
}
