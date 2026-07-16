import type { Dataset, DatasetColumn } from "@/types/dataset.types";
import type { Insight, CorrelationPair, ColumnProfile } from "@/types/insight.types";
import type { PredictiveRun, ForecastPoint } from "@/types/prediction.types";
import type { DecisionCard } from "@/types/decision.types";
import type { RequirementRun } from "@/types/requirement.types";
import type { AgentActivity, PipelineStage } from "@/types/agent.types";
import type { Project } from "@/types/api.types";

export const mockColumns: DatasetColumn[] = [
  { name: "order_id", dataType: "string", nullable: false, missingCount: 0, missingPct: 0, uniqueCount: 12480, sampleValues: ["ORD-10021", "ORD-10022"] },
  { name: "order_date", dataType: "datetime", nullable: false, missingCount: 0, missingPct: 0, uniqueCount: 365, sampleValues: ["2025-11-02", "2025-11-03"] },
  { name: "region", dataType: "categorical", nullable: false, missingCount: 12, missingPct: 0.1, uniqueCount: 6, sampleValues: ["West", "East", "Midwest"] },
  { name: "revenue", dataType: "float", nullable: false, missingCount: 34, missingPct: 0.27, uniqueCount: 9210, sampleValues: ["1204.50", "899.00"], min: 12.4, max: 18420.5, mean: 842.1, stdDev: 612.3 },
  { name: "units", dataType: "integer", nullable: false, missingCount: 0, missingPct: 0, uniqueCount: 340, sampleValues: ["4", "12"], min: 1, max: 500, mean: 18.2, stdDev: 22.6 },
  { name: "churned", dataType: "boolean", nullable: false, missingCount: 0, missingPct: 0, uniqueCount: 2, sampleValues: ["false", "true"] },
];

export const mockDatasets: Dataset[] = [
  {
    id: "ds_orders_2025",
    projectId: "proj_retail",
    name: "orders_q4_2025.csv",
    fileType: "csv",
    sizeBytes: 18_400_000,
    rowCount: 128_402,
    columnCount: 14,
    uploadedAt: new Date(Date.now() - 1000 * 60 * 42).toISOString(),
    status: "ready",
    qualityScore: 87,
    columns: mockColumns,
    duplicateRows: 214,
    missingCells: 1032,
    outlierCount: 58,
  },
  {
    id: "ds_customers_2025",
    projectId: "proj_retail",
    name: "customer_master.xlsx",
    fileType: "xlsx",
    sizeBytes: 6_200_000,
    rowCount: 40_918,
    columnCount: 9,
    uploadedAt: new Date(Date.now() - 1000 * 60 * 60 * 5).toISOString(),
    status: "ready",
    qualityScore: 94,
    columns: mockColumns.slice(0, 4),
    duplicateRows: 12,
    missingCells: 88,
    outlierCount: 6,
  },
];

export const mockProjects: Project[] = [
  {
    id: "proj_retail",
    name: "Retail Performance",
    description: "Quarterly order, revenue, and churn analysis across regions.",
    datasetCount: 2,
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 12).toISOString(),
    updatedAt: new Date(Date.now() - 1000 * 60 * 42).toISOString(),
  },
  {
    id: "proj_ops",
    name: "Fulfillment Ops",
    description: "Warehouse throughput and delivery-time modeling.",
    datasetCount: 1,
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 30).toISOString(),
    updatedAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 2).toISOString(),
  },
];

export const mockInsights: Insight[] = [
  { id: "in_1", datasetId: "ds_orders_2025", category: "trend", title: "Revenue accelerating in the West region", narrative: "West region revenue grew 22% quarter-over-quarter, outpacing all other regions by more than 3x.", confidence: 0.91, createdAt: new Date().toISOString(), relatedColumns: ["region", "revenue"] },
  { id: "in_2", datasetId: "ds_orders_2025", category: "anomaly", title: "Unusual spike in order volume on Nov 14", narrative: "Order volume was 6.2 standard deviations above the trailing 30-day average, concentrated in the Midwest.", confidence: 0.86, createdAt: new Date().toISOString(), relatedColumns: ["order_date", "units"] },
  { id: "in_3", datasetId: "ds_orders_2025", category: "risk", title: "Churn correlates with declining order frequency", narrative: "Customers with a 40%+ drop in monthly order frequency churn at 3.4x the base rate.", confidence: 0.79, createdAt: new Date().toISOString(), relatedColumns: ["churned", "units"] },
  { id: "in_4", datasetId: "ds_orders_2025", category: "opportunity", title: "Bundled SKUs show 18% higher margin", narrative: "Orders containing 3+ SKUs from the same category carry meaningfully higher average margin.", confidence: 0.83, createdAt: new Date().toISOString(), relatedColumns: ["revenue", "units"] },
];

export const mockCorrelations: CorrelationPair[] = [
  { columnA: "revenue", columnB: "units", coefficient: 0.78 },
  { columnA: "revenue", columnB: "churned", coefficient: -0.42 },
  { columnA: "units", columnB: "churned", coefficient: -0.31 },
  { columnA: "revenue", columnB: "region", coefficient: 0.22 },
];

export const mockColumnProfiles: ColumnProfile[] = [
  {
    column: "revenue",
    mean: 842.1,
    median: 610,
    stdDev: 612.3,
    skew: 1.4,
    histogram: [
      { bucket: "0-250", count: 3200 },
      { bucket: "250-500", count: 4100 },
      { bucket: "500-1000", count: 5300 },
      { bucket: "1000-2500", count: 2900 },
      { bucket: "2500+", count: 980 },
    ],
  },
  {
    column: "units",
    mean: 18.2,
    median: 12,
    stdDev: 22.6,
    skew: 2.1,
    histogram: [
      { bucket: "1-5", count: 4800 },
      { bucket: "6-15", count: 5200 },
      { bucket: "16-30", count: 2700 },
      { bucket: "31-60", count: 1100 },
      { bucket: "60+", count: 400 },
    ],
  },
];

function buildForecast(): ForecastPoint[] {
  const points: ForecastPoint[] = [];
  const base = 40000;
  for (let i = 0; i < 18; i++) {
    const date = new Date(2025, 6 + i, 1).toISOString().slice(0, 7);
    const seasonal = Math.sin(i / 2) * 3000;
    const trend = i * 900;
    const actual = i < 12 ? base + trend + seasonal + (Math.random() - 0.5) * 1500 : undefined;
    const forecast = i >= 9 ? base + trend + seasonal : undefined;
    points.push({
      date,
      actual: actual ? Math.round(actual) : undefined,
      forecast: forecast ? Math.round(forecast) : undefined,
      lowerBound: forecast ? Math.round(forecast * 0.9) : undefined,
      upperBound: forecast ? Math.round(forecast * 1.1) : undefined,
    });
  }
  return points;
}

export const mockPredictiveRun: PredictiveRun = {
  id: "run_1",
  datasetId: "ds_orders_2025",
  target: "revenue",
  task: "forecasting",
  status: "complete",
  candidates: [
    { id: "m1", name: "Prophet (seasonal)", task: "forecasting", metric: "MAPE", score: 0.081, trainingTimeSeconds: 4.2, isBest: true },
    { id: "m2", name: "Gradient Boosted Trees", task: "regression", metric: "MAPE", score: 0.104, trainingTimeSeconds: 9.8, isBest: false },
    { id: "m3", name: "Linear Regression", task: "regression", metric: "MAPE", score: 0.163, trainingTimeSeconds: 1.1, isBest: false },
    { id: "m4", name: "Random Forest", task: "regression", metric: "MAPE", score: 0.119, trainingTimeSeconds: 6.4, isBest: false },
  ],
  featureImportance: [
    { feature: "order_month", importance: 0.34 },
    { feature: "region", importance: 0.27 },
    { feature: "units", importance: 0.22 },
    { feature: "promo_flag", importance: 0.11 },
    { feature: "channel", importance: 0.06 },
  ],
  forecast: buildForecast(),
  explanation:
    "Prophet's seasonal model was selected for lowest MAPE (8.1%). Revenue shows a consistent upward trend of roughly $900/month with a recurring bi-monthly seasonal lift, most pronounced in the West region.",
};

export const mockDecisions: DecisionCard[] = [
  { id: "dc_1", title: "Shift ad spend toward West region bundles", area: "revenue", priority: "high", narrative: "West region bundle orders show 18% higher margin and 22% QoQ growth. Reallocating 15% of Midwest ad spend is projected to lift quarterly revenue.", confidence: 0.83, expectedRoiPct: 24, impact: 4, effort: 2, estimatedValue: 186000, actionSteps: ["Pull top 10 bundle SKUs by margin", "Draft West-region campaign brief", "Shift 15% of Midwest budget for 6 weeks", "Re-measure at day 30"], status: "proposed" },
  { id: "dc_2", title: "Launch win-back flow for declining-frequency customers", area: "customer", priority: "critical", narrative: "Customers with 40%+ drop in order frequency churn at 3.4x baseline. An automated win-back sequence could recover a meaningful share before churn.", confidence: 0.79, expectedRoiPct: 31, impact: 5, effort: 3, estimatedValue: 240000, actionSteps: ["Define frequency-drop trigger (40%+ over 60 days)", "Build 3-email win-back sequence", "A/B test incentive vs. no incentive", "Track reactivation rate weekly"], status: "in_progress" },
  { id: "dc_3", title: "Investigate Nov 14 Midwest order spike", area: "risk", priority: "medium", narrative: "A 6.2σ spike in Midwest order volume on Nov 14 doesn't match any known promotion — worth confirming it isn't a data or fraud issue before year-end planning.", confidence: 0.71, expectedRoiPct: 0, impact: 3, effort: 1, estimatedValue: 0, actionSteps: ["Cross-check against promo calendar", "Sample 25 orders for manual review", "Confirm with fulfillment ops"], status: "proposed" },
  { id: "dc_4", title: "Consolidate low-margin SKUs", area: "cost", priority: "low", narrative: "Bottom-quartile SKUs by margin represent 4% of revenue but 11% of SKU management overhead.", confidence: 0.66, expectedRoiPct: 9, impact: 2, effort: 2, estimatedValue: 42000, actionSteps: ["Identify bottom-quartile SKUs by margin", "Review with category managers", "Sunset or reprice over next cycle"], status: "proposed" },
];

export function mockRequirementRun(datasetId: string, requirement: string): RequirementRun {
  return {
    id: `rr_${Date.now()}`,
    datasetId,
    requirement,
    parseMode: "structured",
    createdAt: new Date().toISOString(),
    decisions: [
      {
        id: `dc_mock_${Date.now()}`,
        title: `Recommendation for: ${requirement.slice(0, 60)}`,
        area: "revenue",
        priority: "high",
        narrative:
          "This is a mock recommendation generated offline — connect the backend for tailored, dataset-grounded results.",
        confidence: 0.7,
        expectedRoiPct: 15,
        impact: 4,
        effort: 3,
        estimatedValue: 50000,
        actionSteps: ["Review with the relevant team", "Validate against the dataset", "Assign an owner and timeline"],
        status: "proposed",
      },
    ],
  };
}

export function mockRequirementHistory(datasetId: string): RequirementRun[] {
  return [mockRequirementRun(datasetId, "Increase revenue in the lowest-performing segment")];
}

export const mockAgentActivity: AgentActivity[] = [
  { id: "a1", agent: "dataset_understanding", label: "Profiled orders_q4_2025.csv schema", status: "complete", startedAt: new Date(Date.now() - 1000 * 60 * 40).toISOString(), completedAt: new Date(Date.now() - 1000 * 60 * 39).toISOString() },
  { id: "a2", agent: "data_cleaning", label: "Removed 214 duplicate rows, flagged 1,032 missing cells", status: "complete", startedAt: new Date(Date.now() - 1000 * 60 * 39).toISOString(), completedAt: new Date(Date.now() - 1000 * 60 * 37).toISOString() },
  { id: "a3", agent: "analytics", label: "Computed correlations and trend decomposition", status: "complete", startedAt: new Date(Date.now() - 1000 * 60 * 37).toISOString(), completedAt: new Date(Date.now() - 1000 * 60 * 35).toISOString() },
  { id: "a4", agent: "predictive_analytics", label: "Trained 4 candidate forecasting models", status: "complete", startedAt: new Date(Date.now() - 1000 * 60 * 35).toISOString(), completedAt: new Date(Date.now() - 1000 * 60 * 30).toISOString() },
  { id: "a5", agent: "decision_support", label: "Generating strategic recommendations", status: "running", startedAt: new Date(Date.now() - 1000 * 60 * 2).toISOString() },
  { id: "a6", agent: "executive_summary", label: "Waiting on decision support output", status: "queued", startedAt: new Date().toISOString() },
];

export const mockPipelineStages: PipelineStage[] = [
  { key: "validate", label: "Validate & profile", status: "complete", progress: 100 },
  { key: "clean", label: "Clean & engineer features", status: "complete", progress: 100 },
  { key: "analyze", label: "Descriptive & statistical analysis", status: "complete", progress: 100 },
  { key: "predict", label: "Predictive modeling & forecasting", status: "complete", progress: 100 },
  { key: "decide", label: "Decision recommendations", status: "running", progress: 62 },
  { key: "summarize", label: "Executive summary", status: "queued", progress: 0 },
  { key: "index", label: "Index for retrieval (RAG)", status: "queued", progress: 0 },
];
