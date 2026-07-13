"use client";

import type { LucideIcon } from "lucide-react";
import { ArrowUpRight, ArrowDownRight } from "lucide-react";
import { cn } from "@/utils/cn";

interface KpiCardProps {
  label: string;
  value: string;
  icon?: LucideIcon;
  delta?: number; // percent change, positive = good
  accent?: "signal" | "amber" | "rose";
  hint?: string;
}

export function KpiCard({ label, value, icon: Icon, delta, accent = "signal", hint }: KpiCardProps) {
  const accentClass = {
    signal: "text-signal bg-signal-soft",
    amber: "text-amber bg-amber/15",
    rose: "text-rose bg-rose/15",
  }[accent];

  return (
    <div className="glass-panel scan-hover p-5">
      <div className="flex items-start justify-between">
        <p className="eyebrow">{label}</p>
        {Icon && (
          <span className={cn("flex h-8 w-8 items-center justify-center rounded-lg", accentClass)}>
            <Icon className="h-4 w-4" />
          </span>
        )}
      </div>
      <p className="kpi-value mt-3">{value}</p>
      {(delta !== undefined || hint) && (
        <div className="mt-2 flex items-center gap-1.5 text-xs">
          {delta !== undefined && (
            <span className={cn("flex items-center gap-0.5 font-medium", delta >= 0 ? "text-signal" : "text-rose")}>
              {delta >= 0 ? <ArrowUpRight className="h-3.5 w-3.5" /> : <ArrowDownRight className="h-3.5 w-3.5" />}
              {Math.abs(delta)}%
            </span>
          )}
          {hint && <span className="text-ink-faint">{hint}</span>}
        </div>
      )}
    </div>
  );
}
