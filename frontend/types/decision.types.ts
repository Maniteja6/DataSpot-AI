export type DecisionPriority = "critical" | "high" | "medium" | "low";
export type DecisionArea =
  | "revenue"
  | "cost"
  | "customer"
  | "operations"
  | "marketing"
  | "risk";

export interface DecisionCard {
  id: string;
  title: string;
  area: DecisionArea;
  priority: DecisionPriority;
  narrative: string;
  confidence: number; // 0-1
  expectedRoiPct: number;
  impact: number; // 1-5
  effort: number; // 1-5
  estimatedValue: number; // currency
  actionSteps: string[];
  status: "proposed" | "in_progress" | "done" | "dismissed";
}

export interface ScenarioAssumption {
  id: string;
  label: string;
  value: number;
  min: number;
  max: number;
  unit?: string;
}

export interface ScenarioResult {
  label: string;
  value: number;
}
