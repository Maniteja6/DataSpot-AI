import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { DecisionCard } from "@/types/decision.types";

export function RiskMatrix({ decisions }: { decisions: DecisionCard[] }) {
  const risks = decisions.filter((d) => d.area === "risk");

  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>Critical Risks</CardTitle>
          <CardDescription>Flagged by the Decision Support agent</CardDescription>
        </div>
      </CardHeader>
      {risks.length === 0 ? (
        <p className="text-sm text-ink-faint">No active risks flagged for this dataset.</p>
      ) : (
        <div className="space-y-3">
          {risks.map((r) => (
            <div key={r.id} className="rounded-xl border border-line p-3">
              <div className="mb-1 flex items-center justify-between">
                <p className="text-sm font-medium text-ink">{r.title}</p>
                <Badge variant="rose">{r.priority}</Badge>
              </div>
              <p className="text-xs text-ink-muted">{r.narrative}</p>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}
