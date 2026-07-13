export type AgentName =
  | "dataset_understanding"
  | "data_cleaning"
  | "analytics"
  | "predictive_analytics"
  | "business_intelligence"
  | "decision_support"
  | "executive_summary"
  | "rag_chat";

export type AgentStatus = "idle" | "queued" | "running" | "complete" | "error";

export interface AgentActivity {
  id: string;
  agent: AgentName;
  label: string;
  status: AgentStatus;
  startedAt: string;
  completedAt?: string;
  detail?: string;
}

export interface PipelineStage {
  key: string;
  label: string;
  status: AgentStatus;
  progress: number; // 0-100
}
