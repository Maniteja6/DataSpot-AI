"use client";

import { Area, ComposedChart, Line, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid, Legend } from "recharts";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import type { ForecastPoint } from "@/types/prediction.types";

export function ForecastChart({ data }: { data: ForecastPoint[] }) {
  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>Forecast</CardTitle>
          <CardDescription>Actuals vs. forecast with confidence interval</CardDescription>
        </div>
      </CardHeader>
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{ top: 8, right: 12, left: -12, bottom: 0 }}>
            <defs>
              <linearGradient id="ciFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="rgb(var(--signal))" stopOpacity={0.18} />
                <stop offset="100%" stopColor="rgb(var(--signal))" stopOpacity={0.02} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgb(var(--line))" vertical={false} />
            <XAxis dataKey="date" stroke="rgb(var(--ink-faint))" fontSize={11} tickLine={false} axisLine={false} />
            <YAxis stroke="rgb(var(--ink-faint))" fontSize={11} tickLine={false} axisLine={false} />
            <Tooltip contentStyle={{ background: "rgb(var(--bg-raised))", border: "1px solid rgb(var(--line))", borderRadius: 12, fontSize: 12 }} />
            <Legend wrapperStyle={{ fontSize: 11, color: "rgb(var(--ink-muted))" }} />
            <Area type="monotone" dataKey="upperBound" stroke="none" fill="url(#ciFill)" name="Upper bound" />
            <Area type="monotone" dataKey="lowerBound" stroke="none" fill="rgb(var(--bg))" name="Lower bound" />
            <Line type="monotone" dataKey="actual" stroke="rgb(var(--ink-muted))" strokeWidth={2} dot={false} name="Actual" />
            <Line type="monotone" dataKey="forecast" stroke="rgb(var(--signal))" strokeWidth={2} strokeDasharray="5 3" dot={false} name="Forecast" />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
