export const CHART_PALETTE = [
  "var(--signal)",
  "#6C8CFF",
  "#FFB454",
  "#FF6B81",
  "#B98CFF",
  "#4DD9E8",
];

export function formatCompactNumber(value: number): string {
  return new Intl.NumberFormat("en-US", {
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(value);
}

export function formatPercent(value: number, fractionDigits = 1): string {
  return `${(value * 100).toFixed(fractionDigits)}%`;
}

export function correlationToColor(value: number): string {
  // -1..1 -> rose..surface..signal
  const clamped = Math.max(-1, Math.min(1, value));
  if (clamped >= 0) {
    const alpha = 0.12 + clamped * 0.55;
    return `rgba(52, 232, 176, ${alpha})`;
  }
  const alpha = 0.12 + Math.abs(clamped) * 0.55;
  return `rgba(255, 107, 129, ${alpha})`;
}
