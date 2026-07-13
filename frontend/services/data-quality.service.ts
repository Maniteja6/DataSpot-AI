import { apiClient, withMockFallback } from "./api-client";
import { mockDatasets } from "./mocks/mockData";
import type { Dataset } from "@/types/dataset.types";

export interface QualityIssue {
  id: string;
  type: "missing_values" | "duplicates" | "outliers" | "schema" | "validation";
  column?: string;
  count: number;
  severity: "low" | "medium" | "high";
  suggestion: string;
  resolved: boolean;
}

const mockIssues: QualityIssue[] = [
  { id: "q1", type: "missing_values", column: "revenue", count: 34, severity: "medium", suggestion: "Impute using region-level median revenue.", resolved: true },
  { id: "q2", type: "duplicates", count: 214, severity: "high", suggestion: "Drop duplicate order_id rows, keep most recent.", resolved: true },
  { id: "q3", type: "outliers", column: "units", count: 58, severity: "low", suggestion: "Cap at 99th percentile; flag for manual review above 300 units.", resolved: false },
  { id: "q4", type: "schema", column: "region", count: 12, severity: "medium", suggestion: "Standardize casing and merge 'west'/'West'/'WEST' variants.", resolved: true },
];

export const dataQualityService = {
  getDataset: (id: string) =>
    withMockFallback(
      () => apiClient.get<Dataset>(`/api/v1/data-quality/${id}`),
      () => mockDatasets.find((d) => d.id === id) ?? mockDatasets[0]
    ),

  getIssues: (id: string) =>
    withMockFallback(
      () => apiClient.get<QualityIssue[]>(`/api/v1/data-quality/${id}/issues`),
      () => mockIssues
    ),
};
