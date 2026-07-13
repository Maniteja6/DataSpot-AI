"use client";

import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid } from "recharts";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";

interface LineChartCardProps {
  title: string;
  description?: string;
  data: Record<string, string | number>[];
  xKey: string;
  yKey: string;
  color?: string;
}

export function LineChartCard({ title, description, data, xKey, yKey, color = "rgb(var(--signal))" }: LineChartCardProps) {
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
          <LineChart data={data} margin={{ top: 8, right: 12, left: -12, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgb(var(--line))" vertical={false} />
            <XAxis dataKey={xKey} stroke="rgb(var(--ink-faint))" fontSize={11} tickLine={false} axisLine={false} />
            <YAxis stroke="rgb(var(--ink-faint))" fontSize={11} tickLine={false} axisLine={false} />
            <Tooltip
              contentStyle={{ background: "rgb(var(--bg-raised))", border: "1px solid rgb(var(--line))", borderRadius: 12, fontSize: 12 }}
            />
            <Line type="monotone" dataKey={yKey} stroke={color} strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
