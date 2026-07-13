"use client";

import Link from "next/link";
import { ArrowRight, TrendingUp, Sliders } from "lucide-react";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ConfidenceBadge } from "@/components/shared/ConfidenceBadge";
import { Button } from "@/components/ui/button";
import { formatCurrency } from "@/lib/formatters";
import type { DecisionCard } from "@/types/decision.types";
import { useUpdateDecisionStatus } from "../hooks/useDecisions";

const PRIORITY_VARIANT: Record<DecisionCard["priority"], "rose" | "amber" | "signal" | "neutral"> = {
  critical: "rose",
  high: "amber",
  medium: "signal",
  low: "neutral",
};

export function StrategicRecommendationCard({ decision }: { decision: DecisionCard }) {
  const updateStatus = useUpdateDecisionStatus(decision.id.split("_")[0] ?? "");

  return (
    <Card className="scan-hover">
      <CardHeader>
        <div className="flex items-center gap-2">
          <Badge variant={PRIORITY_VARIANT[decision.priority]}>{decision.priority}</Badge>
          <Badge variant="neutral">{decision.area}</Badge>
        </div>
        <ConfidenceBadge confidence={decision.confidence} />
      </CardHeader>
      <CardTitle className="mb-2 text-base">{decision.title}</CardTitle>
      <p className="text-sm text-ink-muted">{decision.narrative}</p>

      <div className="mt-4 grid grid-cols-3 gap-3 text-center">
        <div className="rounded-lg bg-bg-raised/60 py-2">
          <p className="flex items-center justify-center gap-1 text-sm font-medium text-signal">
            <TrendingUp className="h-3.5 w-3.5" /> {decision.expectedRoiPct}%
          </p>
          <p className="text-[10px] text-ink-faint">Expected ROI</p>
        </div>
        <div className="rounded-lg bg-bg-raised/60 py-2">
          <p className="text-sm font-medium text-ink">{formatCurrency(decision.estimatedValue)}</p>
          <p className="text-[10px] text-ink-faint">Est. value</p>
        </div>
        <div className="rounded-lg bg-bg-raised/60 py-2">
          <p className="text-sm font-medium text-ink">{decision.impact}/5 · {decision.effort}/5</p>
          <p className="text-[10px] text-ink-faint">Impact / Effort</p>
        </div>
      </div>

      <ul className="mt-4 space-y-1.5">
        {decision.actionSteps.slice(0, 3).map((step, i) => (
          <li key={i} className="flex items-start gap-2 text-xs text-ink-muted">
            <ArrowRight className="mt-0.5 h-3 w-3 shrink-0 text-signal" />
            {step}
          </li>
        ))}
      </ul>

      <div className="mt-4 flex gap-2">
        <Button
          size="sm"
          variant="secondary"
          onClick={() => updateStatus.mutate({ id: decision.id, status: "in_progress" })}
        >
          Track action
        </Button>
        <Button
          size="sm"
          variant="ghost"
          onClick={() => updateStatus.mutate({ id: decision.id, status: "dismissed" })}
        >
          Dismiss
        </Button>
        <Link href={`/decision-making/scenario/${decision.id}`} className="ml-auto">
          <Button size="sm" variant="ghost">
            <Sliders className="h-3.5 w-3.5" /> Simulate
          </Button>
        </Link>
      </div>
    </Card>
  );
}
