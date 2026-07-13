"use client";

import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip, Legend } from "recharts";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { CHART_PALETTE } from "@/utils/chart-helpers";

interface PieChartCardProps {
  title: string;
  description?: string;
  data: { name: string; value: number }[];
}

export function PieChartCard({ title, description, data }: PieChartCardProps) {
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
          <PieChart>
            <Pie data={data} dataKey="value" nameKey="name" innerRadius={55} outerRadius={85} paddingAngle={2}>
              {data.map((_, i) => (
                <Cell key={i} fill={CHART_PALETTE[i % CHART_PALETTE.length]} stroke="rgb(var(--bg-surface))" strokeWidth={2} />
              ))}
            </Pie>
            <Tooltip contentStyle={{ background: "rgb(var(--bg-raised))", border: "1px solid rgb(var(--line))", borderRadius: 12, fontSize: 12 }} />
            <Legend wrapperStyle={{ fontSize: 11, color: "rgb(var(--ink-muted))" }} />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
