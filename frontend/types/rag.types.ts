export type CitationSourceType =
  | "dataset_profile"
  | "cleaning_log"
  | "analytics_summary"
  | "forecast_summary"
  | "decision_recommendation"
  | "executive_summary"
  | "conversation_history";

export interface CitationSource {
  id: string;
  type: CitationSourceType;
  title: string;
  snippet: string;
  datasetId?: string;
  relevanceScore: number; // 0-1
}

export interface RetrievedChunk {
  id: string;
  text: string;
  source: CitationSource;
}

export interface RagAnswer {
  answer: string;
  citations: CitationSource[];
  retrievedChunks: RetrievedChunk[];
}
