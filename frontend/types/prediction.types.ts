export type ModelTask = "regression" | "classification" | "clustering" | "forecasting";

export interface ModelCandidate {
  id: string;
  name: string;
  task: ModelTask;
  metric: string;
  score: number;
  trainingTimeSeconds: number;
  isBest: boolean;
}

export interface FeatureImportance {
  feature: string;
  importance: number; // 0-1
}

export interface ForecastPoint {
  date: string;
  actual?: number;
  forecast?: number;
  lowerBound?: number;
  upperBound?: number;
}

export interface PredictionRow {
  id: string;
  [field: string]: string | number;
}

export interface PredictiveRun {
  id: string;
  datasetId: string;
  target: string;
  task: ModelTask;
  status: "idle" | "running" | "complete" | "error";
  candidates: ModelCandidate[];
  featureImportance: FeatureImportance[];
  forecast: ForecastPoint[];
  explanation: string;
}
