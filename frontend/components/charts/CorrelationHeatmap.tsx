"use client";

import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { correlationToColor } from "@/utils/chart-helpers";
import type { CorrelationPair } from "@/types/insight.types";

export function CorrelationHeatmap({ pairs }: { pairs: CorrelationPair[] }) {
  const columns = Array.from(new Set(pairs.flatMap((p) => [p.columnA, p.columnB])));

  function lookup(a: string, b: string): number {
    if (a === b) return 1;
    const found = pairs.find(
      (p) => (p.columnA === a && p.columnB === b) || (p.columnA === b && p.columnB === a)
    );
    return found?.coefficient ?? 0;
  }

  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>Correlation Heatmap</CardTitle>
          <CardDescription>Pairwise correlation across numeric columns</CardDescription>
        </div>
      </CardHeader>
      <div className="overflow-x-auto">
        <table className="w-full border-separate" style={{ borderSpacing: 4 }}>
          <thead>
            <tr>
              <th className="w-20" />
              {columns.map((c) => (
                <th key={c} className="pb-1 text-[10px] font-mono uppercase text-ink-faint">
                  {c}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {columns.map((rowCol) => (
              <tr key={rowCol}>
                <td className="pr-2 text-[10px] font-mono uppercase text-ink-faint">{rowCol}</td>
                {columns.map((colCol) => {
                  const value = lookup(rowCol, colCol);
                  return (
                    <td key={colCol} className="p-0">
                      <div
                        className="flex h-11 w-11 items-center justify-center rounded-lg text-[11px] font-mono text-ink"
                        style={{ background: correlationToColor(value) }}
                        title={`${rowCol} × ${colCol}: ${value.toFixed(2)}`}
                      >
                        {value.toFixed(2)}
                      </div>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}
