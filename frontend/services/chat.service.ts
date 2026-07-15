import { apiClient, withMockFallback } from "./api-client";
import type { ChatResponse } from "@/types/rag.types";

function mockChatResponse(question: string, conversationId?: string): ChatResponse {
  return {
    answer: `On "${question}":\n- Revenue is trending up ~$900/month, with the West region outperforming.\n- Revenue and units show a 0.78 correlation.\n- Forecast shows continued upward trend with bi-monthly seasonality, MAPE 8.1%.`,
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
    conversationId: conversationId ?? `mock_conv_${Date.now()}`,
  };
}

export const chatService = {
  ask: (question: string, datasetId?: string, conversationId?: string) =>
    withMockFallback(
      () =>
        apiClient.post<ChatResponse>("/api/v1/chat", {
          question,
          datasetId,
          conversationId,
        }),
      () => mockChatResponse(question, conversationId)
    ),
};