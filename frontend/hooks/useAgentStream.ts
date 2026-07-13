"use client";

import { useEffect, useState } from "react";
import type { AgentActivity } from "@/types/agent.types";
import { mockAgentActivity } from "@/services/mocks/mockData";

/**
 * Streams agent activity events for the workspace timeline.
 * Live implementation subscribes to a server-sent-events endpoint backed by
 * AgentCore observability tracing; this mock version simulates a live feed
 * so the Dashboard's Agent Status panel always feels alive during a demo.
 */
export function useAgentStream() {
  const [activity, setActivity] = useState<AgentActivity[]>(mockAgentActivity);

  useEffect(() => {
    const interval = setInterval(() => {
      setActivity((prev) => {
        const running = prev.find((a) => a.status === "running");
        if (!running) return prev;
        return prev.map((a) =>
          a.id === running.id ? { ...a, status: "complete", completedAt: new Date().toISOString() } : a
        );
      });
    }, 6000);
    return () => clearInterval(interval);
  }, []);

  return activity;
}
