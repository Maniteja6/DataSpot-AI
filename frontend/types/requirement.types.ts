import type { DecisionCard } from "./decision.types";

export type RequirementParseMode = "structured" | "fallback_single_card" | "degraded_no_llm";

export interface RequirementRun {
  id: string;
  datasetId: string;
  requirement: string;
  decisions: DecisionCard[];
  parseMode: RequirementParseMode;
  createdAt: string;
}
