"use client";

import { Card, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export default function ProfilePage() {
  return (
    <div className="max-w-2xl space-y-6 animate-fade-up">
      <Card>
        <div className="mb-5 flex items-center gap-4">
          <div className="h-16 w-16 rounded-full bg-gradient-to-br from-signal/60 to-bg-raised" />
          <div>
            <p className="font-display text-lg font-medium text-ink">Analyst Workspace</p>
            <p className="text-xs text-ink-faint">Prototype session · no login required</p>
          </div>
        </div>
        <div className="grid gap-3 sm:grid-cols-2">
          <div>
            <label className="mb-1.5 block text-xs text-ink-faint">Display name</label>
            <Input defaultValue="Data Analyst" />
          </div>
          <div>
            <label className="mb-1.5 block text-xs text-ink-faint">Email</label>
            <Input defaultValue="analyst@dataspot.ai" />
          </div>
        </div>
        <Button className="mt-4" size="sm">Save changes</Button>
      </Card>

      <Card>
        <CardTitle className="mb-1">About this prototype</CardTitle>
        <CardDescription>
          DataSpot AI runs without authentication in this build — every session is a fresh workspace.
          Connect a real identity provider before deploying beyond a demo environment.
        </CardDescription>
      </Card>
    </div>
  );
}
