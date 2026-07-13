"use client";

import { CartesianGrid, ResponsiveContainer, Scatter, ScatterChart, Tooltip, XAxis, YAxis, ZAxis } from "recharts";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";

interface ScatterPlotProps {
  title: string;
  description?: string;
  data: { x: number; y: number; z?: number }[];
  xLabel: string;
  yLabel: string;
}

export function ScatterPlot({ title, description, data, xLabel, yLabel }: ScatterPlotProps) {
  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>{title}</CardTitle>
          {description && <CardDescription>{description}</CardDescription>}
        </div>
      </CardHeader>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 8, right: 12, left: -12, bottom: 0 }}>
            <CartesianGrid stroke="rgb(var(--line))" />
            <XAxis type="number" dataKey="x" name={xLabel} stroke="rgb(var(--ink-faint))" fontSize={11} tickLine={false} axisLine={false} />
            <YAxis type="number" dataKey="y" name={yLabel} stroke="rgb(var(--ink-faint))" fontSize={11} tickLine={false} axisLine={false} />
            <ZAxis type="number" dataKey="z" range={[40, 160]} />
            <Tooltip
              cursor={{ strokeDasharray: "3 3" }}
              contentStyle={{ background: "rgb(var(--bg-raised))", border: "1px solid rgb(var(--line))", borderRadius: 12, fontSize: 12 }}
            />
            <Scatter data={data} fill="rgb(var(--signal))" fillOpacity={0.7} />
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
