const ACCEPTED_EXTENSIONS = [".csv", ".xlsx", ".xls"];
const MAX_FILE_SIZE_BYTES = 200 * 1024 * 1024; // 200MB, matches upload zone copy

export interface FileValidationResult {
  valid: boolean;
  error?: string;
}

export function validateDatasetFile(file: File): FileValidationResult {
  const lowerName = file.name.toLowerCase();
  const hasValidExtension = ACCEPTED_EXTENSIONS.some((ext) =>
    lowerName.endsWith(ext)
  );

  if (!hasValidExtension) {
    return {
      valid: false,
      error: "Only CSV and Excel (.xlsx, .xls) files are supported.",
    };
  }

  if (file.size > MAX_FILE_SIZE_BYTES) {
    return {
      valid: false,
      error: "File exceeds the 200MB limit for this workspace.",
    };
  }

  if (file.size === 0) {
    return { valid: false, error: "This file is empty." };
  }

  return { valid: true };
}

export function formatBytes(bytes: number): string {
  if (bytes === 0) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  const exponent = Math.min(
    Math.floor(Math.log(bytes) / Math.log(1024)),
    units.length - 1
  );
  const value = bytes / Math.pow(1024, exponent);
  return `${exponent === 0 ? value : value.toFixed(1)} ${units[exponent]}`;
}
