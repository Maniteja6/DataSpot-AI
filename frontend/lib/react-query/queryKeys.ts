export const queryKeys = {
  datasets: {
    all: ["datasets"] as const,
    detail: (id: string) => ["datasets", id] as const,
  },
  projects: {
    all: ["projects"] as const,
    detail: (id: string) => ["projects", id] as const,
  },
  insights: {
    byDataset: (datasetId: string) => ["insights", datasetId] as const,
  },
  predictive: {
    byDataset: (datasetId: string) => ["predictive", datasetId] as const,
  },
  decisions: {
    byDataset: (datasetId: string) => ["decisions", datasetId] as const,
  },
  pipeline: {
    status: (datasetId: string) => ["pipeline", "status", datasetId] as const,
  },
  chat: {
    history: ["chat", "history"] as const,
  },
} as const;
