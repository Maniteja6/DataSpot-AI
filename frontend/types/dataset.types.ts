export type ColumnDataType =
  | "integer"
  | "float"
  | "string"
  | "boolean"
  | "datetime"
  | "categorical";

export interface DatasetColumn {
  name: string;
  dataType: ColumnDataType;
  nullable: boolean;
  missingCount: number;
  missingPct: number;
  uniqueCount: number;
  sampleValues: string[];
  min?: number;
  max?: number;
  mean?: number;
  stdDev?: number;
}

export interface Dataset {
  id: string;
  projectId: string;
  name: string;
  fileType: "csv" | "xlsx";
  sizeBytes: number;
  rowCount: number;
  columnCount: number;
  uploadedAt: string;
  status: "uploading" | "processing" | "ready" | "error";
  qualityScore: number; // 0-100
  columns: DatasetColumn[];
  duplicateRows: number;
  missingCells: number;
  outlierCount: number;
}

export interface DatasetPreviewRow {
  [column: string]: string | number | boolean | null;
}
