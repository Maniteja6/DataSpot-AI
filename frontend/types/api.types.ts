export interface ApiError {
  status: number;
  message: string;
  detail?: string;
}

export interface Paginated<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: import("./rag.types").CitationSource[];
  createdAt: string;
}

export interface Project {
  id: string;
  name: string;
  description: string;
  datasetCount: number;
  createdAt: string;
  updatedAt: string;
}
