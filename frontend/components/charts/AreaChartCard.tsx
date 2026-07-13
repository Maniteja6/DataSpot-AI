"use client";

import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid } from "recharts";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";

interface AreaChartCardProps {
  title: string;
  description?: string;
  data: Record<string, string | number>[];
  xKey: string;
  yKey: string;
}

export function AreaChartCard({ title, description, data, xKey, yKey }: AreaChartCardProps) {
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
          <AreaChart data={data} margin={{ top: 8, right: 12, left: -12, bottom: 0 }}>
            <defs>
              <linearGradient id="areaFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="rgb(var(--signal))" stopOpacity={0.35} />
                <stop offset="100%" stopColor="rgb(var(--signal))" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgb(var(--line))" vertical={false} />
            <XAxis dataKey={xKey} stroke="rgb(var(--ink-faint))" fontSize={11} tickLine={false} axisLine={false} />
            <YAxis stroke="rgb(var(--ink-faint))" fontSize={11} tickLine={false} axisLine={false} />
            <Tooltip contentStyle={{ background: "rgb(var(--bg-raised))", border: "1px solid rgb(var(--line))", borderRadius: 12, fontSize: 12 }} />
            <Area type="monotone" dataKey={yKey} stroke="rgb(var(--signal))" strokeWidth={2} fill="url(#areaFill)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
