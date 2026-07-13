export type InsightCategory =
  | "opportunity"
  | "risk"
  | "anomaly"
  | "trend"
  | "correlation"
  | "prediction"
  | "recommendation"
  | "executive_observation";

export interface Insight {
  id: string;
  datasetId: string;
  category: InsightCategory;
  title: string;
  narrative: string;
  confidence: number; // 0-1
  createdAt: string;
  relatedColumns: string[];
}

export interface CorrelationPair {
  columnA: string;
  columnB: string;
  coefficient: number; // -1..1
}

export interface DistributionBucket {
  bucket: string;
  count: number;
  [key: string]: string | number;
}

export interface ColumnProfile {
  column: string;
  histogram: DistributionBucket[];
  mean?: number;
  median?: number;
  stdDev?: number;
  skew?: number;
}
