import { PriorityMatrix } from "@/components/charts/PriorityMatrix";
import type { DecisionCard } from "@/types/decision.types";

// Thin, semantically-named wrapper around the shared PriorityMatrix chart so
// the Decision Making Dashboard can reference "Impact vs Effort" explicitly.
export function ImpactEffortMatrix({ decisions }: { decisions: DecisionCard[] }) {
  return <PriorityMatrix decisions={decisions} />;
}
