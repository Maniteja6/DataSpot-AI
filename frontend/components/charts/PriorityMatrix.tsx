"use client";

import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import type { DecisionCard } from "@/types/decision.types";
import { cn } from "@/utils/cn";

const PRIORITY_COLOR: Record<DecisionCard["priority"], string> = {
  critical: "bg-rose",
  high: "bg-amber",
  medium: "bg-signal",
  low: "bg-ink-faint",
};

export function PriorityMatrix({ decisions }: { decisions: DecisionCard[] }) {
  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>Impact vs. Effort Matrix</CardTitle>
          <CardDescription>Bubble size reflects estimated business value</CardDescription>
        </div>
      </CardHeader>
      <div className="relative h-72 rounded-xl border border-line bg-bg-surface/40">
        {/* axis labels */}
        <span className="absolute bottom-1 left-1/2 -translate-x-1/2 text-[10px] font-mono uppercase text-ink-faint">
          Effort →
        </span>
        <span className="absolute left-1 top-1/2 -translate-y-1/2 -rotate-90 text-[10px] font-mono uppercase text-ink-faint">
          Impact →
        </span>
        <div className="absolute left-1/2 top-0 h-full w-px bg-line" />
        <div className="absolute left-0 top-1/2 w-full h-px bg-line" />

        {decisions.map((d) => {
          const left = (d.effort / 5) * 90 + 5;
          const bottom = (d.impact / 5) * 90 + 5;
          const size = 28 + Math.min(40, d.estimatedValue / 8000);
          return (
            <div
              key={d.id}
              title={d.title}
              className={cn(
                "absolute flex -translate-x-1/2 translate-y-1/2 items-center justify-center rounded-full text-[9px] font-mono text-bg opacity-90 transition-transform hover:scale-110",
                PRIORITY_COLOR[d.priority]
              )}
              style={{ left: `${left}%`, bottom: `${bottom}%`, width: size, height: size }}
            >
              {d.expectedRoiPct}%
            </div>
          );
        })}
      </div>
    </Card>
  );
}
