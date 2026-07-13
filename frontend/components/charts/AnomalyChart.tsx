"use client";

import { Line, LineChart, ResponsiveContainer, Scatter, ComposedChart, Tooltip, XAxis, YAxis, CartesianGrid } from "recharts";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";

interface AnomalyPoint {
  x: string;
  value: number;
  isAnomaly?: boolean;
}

export function AnomalyChart({ data }: { data: AnomalyPoint[] }) {
  const anomalies = data.filter((d) => d.isAnomaly);

  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>Anomaly Detection</CardTitle>
          <CardDescription>Values flagged outside the expected range</CardDescription>
        </div>
      </CardHeader>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{ top: 8, right: 12, left: -12, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgb(var(--line))" vertical={false} />
            <XAxis dataKey="x" stroke="rgb(var(--ink-faint))" fontSize={11} tickLine={false} axisLine={false} />
            <YAxis stroke="rgb(var(--ink-faint))" fontSize={11} tickLine={false} axisLine={false} />
            <Tooltip contentStyle={{ background: "rgb(var(--bg-raised))", border: "1px solid rgb(var(--line))", borderRadius: 12, fontSize: 12 }} />
            <Line type="monotone" dataKey="value" stroke="rgb(var(--ink-muted))" strokeWidth={2} dot={false} />
            <Scatter data={anomalies} dataKey="value" fill="rgb(var(--rose))" shape="circle" />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
