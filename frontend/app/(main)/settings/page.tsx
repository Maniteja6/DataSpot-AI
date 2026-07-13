"use client";

import { Card, CardTitle, CardDescription } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Input } from "@/components/ui/input";
import { useThemeStore } from "@/stores/useThemeStore";
import { useState } from "react";

export default function SettingsPage() {
  const { theme, setTheme } = useThemeStore();
  const [apiUrl, setApiUrl] = useState(process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000");
  const [notifications, setNotifications] = useState(true);
  const [autoIndex, setAutoIndex] = useState(true);

  return (
    <div className="max-w-2xl space-y-6 animate-fade-up">
      <Card>
        <CardTitle className="mb-1">Appearance</CardTitle>
        <CardDescription className="mb-4">Choose how DataSpot AI looks on this device</CardDescription>
        <div className="flex items-center justify-between">
          <p className="text-sm text-ink">Dark mode</p>
          <Switch checked={theme === "dark"} onCheckedChange={(v) => setTheme(v ? "dark" : "light")} />
        </div>
      </Card>

      <Card>
        <CardTitle className="mb-1">Backend connection</CardTitle>
        <CardDescription className="mb-4">FastAPI / AWS Bedrock AgentCore endpoint</CardDescription>
        <label className="mb-1.5 block text-xs text-ink-faint">API base URL</label>
        <Input value={apiUrl} onChange={(e) => setApiUrl(e.target.value)} />
      </Card>

      <Card>
        <CardTitle className="mb-1">Notifications</CardTitle>
        <CardDescription className="mb-4">Pipeline and agent activity alerts</CardDescription>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <p className="text-sm text-ink">Notify when pipeline completes</p>
            <Switch checked={notifications} onCheckedChange={setNotifications} />
          </div>
          <div className="flex items-center justify-between">
            <p className="text-sm text-ink">Auto-index new datasets for RAG chat</p>
            <Switch checked={autoIndex} onCheckedChange={setAutoIndex} />
          </div>
        </div>
      </Card>
    </div>
  );
}
