"use client";

import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid, Cell } from "recharts";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { CHART_PALETTE } from "@/utils/chart-helpers";

interface BarChartCardProps {
  title: string;
  description?: string;
  data: Record<string, string | number>[];
  xKey: string;
  yKey: string;
  multiColor?: boolean;
}

export function BarChartCard({ title, description, data, xKey, yKey, multiColor }: BarChartCardProps) {
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
          <BarChart data={data} margin={{ top: 8, right: 12, left: -12, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgb(var(--line))" vertical={false} />
            <XAxis dataKey={xKey} stroke="rgb(var(--ink-faint))" fontSize={11} tickLine={false} axisLine={false} />
            <YAxis stroke="rgb(var(--ink-faint))" fontSize={11} tickLine={false} axisLine={false} />
            <Tooltip
              cursor={{ fill: "var(--signal-soft)" }}
              contentStyle={{ background: "rgb(var(--bg-raised))", border: "1px solid rgb(var(--line))", borderRadius: 12, fontSize: 12 }}
            />
            <Bar dataKey={yKey} radius={[6, 6, 0, 0]}>
              {data.map((_, i) => (
                <Cell key={i} fill={multiColor ? CHART_PALETTE[i % CHART_PALETTE.length] : "rgb(var(--signal))"} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
