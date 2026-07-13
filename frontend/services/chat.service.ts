import { apiClient, withMockFallback } from "./api-client";
import type { RagAnswer } from "@/types/rag.types";

function mockRagAnswer(question: string): RagAnswer {
  return {
    answer: `Based on the indexed profile of orders_q4_2025.csv, here's what's grounded in your data: revenue is trending up ~$900/month with West region outperforming. Your question — "${question}" — is most directly supported by the analytics summary and the latest forecast run.`,
    citations: [
      {
        id: "c1",
        type: "analytics_summary",
        title: "Analytics Agent — correlation & trend summary",
        snippet: "Revenue and units show a 0.78 correlation; West region grew 22% QoQ.",
        datasetId: "ds_orders_2025",
        relevanceScore: 0.91,
      },
      {
        id: "c2",
        type: "forecast_summary",
        title: "Predictive Analytics Agent — Prophet forecast",
        snippet: "Forecast shows continued upward trend with bi-monthly seasonality, MAPE 8.1%.",
        datasetId: "ds_orders_2025",
        relevanceScore: 0.84,
      },
    ],
    retrievedChunks: [],
  };
}

export const chatService = {
  ask: (question: string, datasetId?: string) =>
    withMockFallback(
      () => apiClient.post<RagAnswer>("/api/v1/chat", { question, datasetId }),
      () => mockRagAnswer(question)
    ),
};
