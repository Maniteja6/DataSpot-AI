import { Badge } from "@/components/ui/badge";

export function ConfidenceBadge({ confidence }: { confidence: number }) {
  const pct = Math.round(confidence * 100);
  const variant = pct >= 80 ? "signal" : pct >= 60 ? "amber" : "rose";
  return <Badge variant={variant}>{pct}% confidence</Badge>;
}
