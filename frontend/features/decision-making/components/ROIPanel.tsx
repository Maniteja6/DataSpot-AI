import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { formatCurrency } from "@/lib/formatters";
import type { DecisionCard } from "@/types/decision.types";

export function ROIPanel({ decisions }: { decisions: DecisionCard[] }) {
  const totalValue = decisions.reduce((sum, d) => sum + d.estimatedValue, 0);
  const avgRoi = decisions.length
    ? Math.round(decisions.reduce((sum, d) => sum + d.expectedRoiPct, 0) / decisions.length)
    : 0;

  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>Business Value Estimation</CardTitle>
          <CardDescription>Aggregated across active recommendations</CardDescription>
        </div>
      </CardHeader>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <p className="kpi-value">{formatCurrency(totalValue)}</p>
          <p className="eyebrow mt-1">Total estimated value</p>
        </div>
        <div>
          <p className="kpi-value">{avgRoi}%</p>
          <p className="eyebrow mt-1">Average expected ROI</p>
        </div>
      </div>
    </Card>
  );
}
