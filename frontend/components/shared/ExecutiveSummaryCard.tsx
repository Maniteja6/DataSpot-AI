import { FileText } from "lucide-react";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";

interface ExecutiveSummaryCardProps {
  findings: string[];
  risks: string[];
  recommendations: string[];
}

export function ExecutiveSummaryCard({ findings, risks, recommendations }: ExecutiveSummaryCardProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <FileText className="h-4 w-4 text-signal" />
          <CardTitle>Executive Summary</CardTitle>
        </div>
      </CardHeader>
      <div className="grid gap-5 md:grid-cols-3">
        <div>
          <p className="eyebrow mb-2">Key Findings</p>
          {findings.length > 0 ? (
            <ul className="space-y-1.5 text-sm text-ink-muted">
              {findings.map((f, i) => <li key={i} className="pl-3 border-l border-signal/40">{f}</li>)}
            </ul>
          ) : (
            <p className="text-sm text-ink-faint">Not enough data yet.</p>
          )}
        </div>
        <div>
          <p className="eyebrow mb-2">Risks</p>
          {risks.length > 0 ? (
            <ul className="space-y-1.5 text-sm text-ink-muted">
              {risks.map((r, i) => <li key={i} className="pl-3 border-l border-rose/40">{r}</li>)}
            </ul>
          ) : (
            <p className="text-sm text-ink-faint">Not enough data yet.</p>
          )}
        </div>
        <div>
          <p className="eyebrow mb-2">Recommendations</p>
          {recommendations.length > 0 ? (
            <ul className="space-y-1.5 text-sm text-ink-muted">
              {recommendations.map((r, i) => <li key={i} className="pl-3 border-l border-amber/40">{r}</li>)}
            </ul>
          ) : (
            <p className="text-sm text-ink-faint">Not enough data yet.</p>
          )}
        </div>
      </div>
    </Card>
  );
}
