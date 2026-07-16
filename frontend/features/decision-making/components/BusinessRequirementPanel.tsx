"use client";

import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { formatRelativeTime } from "@/lib/formatters";
import { BusinessRequirementForm } from "./BusinessRequirementForm";
import { StrategicRecommendationCard } from "./StrategicRecommendationCard";
import { useRequirementHistory, useSubmitRequirement } from "../hooks/useRequirementRuns";

export function BusinessRequirementPanel({ datasetId }: { datasetId: string | null }) {
  const { data: history, isLoading } = useRequirementHistory(datasetId);
  const submit = useSubmitRequirement(datasetId);
  const [lastRequirement, setLastRequirement] = useState("");

  const handleSubmit = (requirement: string) => {
    setLastRequirement(requirement);
    submit.mutate(requirement);
  };

  return (
    <div className="space-y-6">
      <Card>
        <p className="eyebrow mb-3">State a business goal</p>
        <BusinessRequirementForm onSubmit={handleSubmit} isPending={submit.isPending} />
      </Card>

      {submit.isPending && (
        <div className="grid gap-4 md:grid-cols-2">
          <Skeleton className="h-64" />
          <Skeleton className="h-64" />
        </div>
      )}

      {submit.isError && (
        <div className="flex items-center justify-between rounded-xl border border-rose/30 bg-rose/10 px-4 py-3 text-sm text-rose">
          <span>Couldn't generate recommendations. The backend may be unreachable.</span>
          <Button size="sm" variant="ghost" onClick={() => submit.mutate(lastRequirement)}>
            Try again
          </Button>
        </div>
      )}

      {isLoading ? (
        <Skeleton className="h-40" />
      ) : !history || history.length === 0 ? (
        !submit.isPending && (
          <p className="text-sm text-ink-faint">No business requirements submitted yet for this dataset.</p>
        )
      ) : (
        <div className="space-y-6">
          {history.map((run) => (
            <div key={run.id}>
              <div className="mb-3 flex items-baseline justify-between">
                <p className="text-sm font-medium text-ink">&ldquo;{run.requirement}&rdquo;</p>
                <p className="text-xs text-ink-faint">{formatRelativeTime(run.createdAt)}</p>
              </div>
              <div className="grid gap-4 md:grid-cols-2">
                {run.decisions.map((d) => (
                  <StrategicRecommendationCard key={d.id} decision={d} readOnly />
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
