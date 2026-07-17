"use client";

import { useDatasets } from "@/features/datasets/hooks/useDatasets";
import { useDecisions, useUpdateDecisionStatus } from "@/features/decision-making/hooks/useDecisions";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { InsightsSkeleton } from "@/components/skeletons/InsightsSkeleton";
import { EmptyState } from "@/components/shared/EmptyState";
import { ListChecks } from "lucide-react";
import type { DecisionCard } from "@/types/decision.types";

const COLUMNS: { key: DecisionCard["status"]; label: string }[] = [
  { key: "proposed", label: "Proposed" },
  { key: "in_progress", label: "In Progress" },
  { key: "done", label: "Done" },
  { key: "dismissed", label: "Dismissed" },
];

export default function ActionTrackingPage() {
  const { data: datasets } = useDatasets();
  const datasetId = datasets?.[0]?.id ?? null;
  const { data: decisions, isLoading } = useDecisions(datasetId ?? "");
  const updateStatus = useUpdateDecisionStatus(datasetId ?? "");

  if (!datasetId) {
    return (
      <EmptyState
        icon={ListChecks}
        title="No dataset yet"
        description="Upload a dataset from the Dashboard to track decision actions."
      />
    );
  }

  if (isLoading || !decisions) return <InsightsSkeleton />;

  return (
    <div className="grid gap-4 lg:grid-cols-4 animate-fade-up">
      {COLUMNS.map((col) => (
        <div key={col.key}>
          <p className="eyebrow mb-3">{col.label} · {decisions.filter((d) => d.status === col.key).length}</p>
          <div className="space-y-3">
            {decisions
              .filter((d) => d.status === col.key)
              .map((d) => (
                <Card key={d.id} className="p-4">
                  <CardHeader className="mb-2">
                    <Badge variant="neutral">{d.area}</Badge>
                  </CardHeader>
                  <CardTitle className="mb-2 text-sm">{d.title}</CardTitle>
                  <div className="flex flex-wrap gap-1.5">
                    {COLUMNS.filter((c) => c.key !== col.key).map((c) => (
                      <button
                        key={c.key}
                        onClick={() => updateStatus.mutate({ id: d.id, status: c.key })}
                        className="rounded-full border border-line px-2 py-0.5 text-[10px] text-ink-faint hover:border-signal/50 hover:text-signal"
                      >
                        → {c.label}
                      </button>
                    ))}
                  </div>
                </Card>
              ))}
            {decisions.filter((d) => d.status === col.key).length === 0 && (
              <p className="rounded-xl border border-dashed border-line p-4 text-center text-xs text-ink-faint">
                Nothing here
              </p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
