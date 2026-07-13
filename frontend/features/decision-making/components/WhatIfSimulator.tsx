"use client";

import { useState } from "react";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { formatCurrency } from "@/lib/formatters";
import { useRunScenario } from "../hooks/useDecisions";
import type { ScenarioAssumption } from "@/types/decision.types";

const DEFAULT_ASSUMPTIONS: ScenarioAssumption[] = [
  { id: "budget_shift", label: "Ad budget reallocated to West region", value: 15, min: 0, max: 40, unit: "%" },
  { id: "conversion_lift", label: "Assumed conversion lift", value: 8, min: 0, max: 25, unit: "%" },
];

export function WhatIfSimulator({ decisionId }: { decisionId: string }) {
  const [assumptions, setAssumptions] = useState(DEFAULT_ASSUMPTIONS);
  const runScenario = useRunScenario(decisionId);

  function updateAssumption(id: string, value: number) {
    setAssumptions((prev) => prev.map((a) => (a.id === id ? { ...a, value } : a)));
  }

  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>What-If Simulator</CardTitle>
          <CardDescription>Adjust assumptions to project business impact</CardDescription>
        </div>
      </CardHeader>

      <div className="space-y-4">
        {assumptions.map((a) => (
          <div key={a.id}>
            <div className="mb-1 flex justify-between text-xs text-ink-muted">
              <span>{a.label}</span>
              <span className="font-mono text-signal">{a.value}{a.unit}</span>
            </div>
            <input
              type="range"
              min={a.min}
              max={a.max}
              value={a.value}
              onChange={(e) => updateAssumption(a.id, Number(e.target.value))}
              className="w-full accent-[rgb(var(--signal))]"
            />
          </div>
        ))}

        <button
          onClick={() => runScenario.mutate(assumptions)}
          className="w-full rounded-xl bg-signal py-2.5 text-sm font-medium text-[#04140f] hover:brightness-110"
        >
          Run scenario
        </button>

        {runScenario.data && (
          <div className="rounded-xl bg-signal-soft p-3 text-center">
            <p className="text-xs text-ink-faint">Projected business value</p>
            <p className="font-display text-xl font-medium text-signal">
              {formatCurrency(runScenario.data.projectedValue)}
            </p>
          </div>
        )}
      </div>
    </Card>
  );
}
