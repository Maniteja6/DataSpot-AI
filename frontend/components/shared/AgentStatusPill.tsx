import type { AgentStatus } from "@/types/agent.types";
import { cn } from "@/utils/cn";

const STATUS_CONFIG: Record<AgentStatus, { label: string; className: string }> = {
  idle: { label: "Idle", className: "bg-bg-raised text-ink-faint" },
  queued: { label: "Queued", className: "bg-bg-raised text-ink-muted" },
  running: { label: "Running", className: "bg-signal-soft text-signal" },
  complete: { label: "Complete", className: "bg-signal-soft text-signal" },
  error: { label: "Error", className: "bg-rose/15 text-rose" },
};

export function AgentStatusPill({ status }: { status: AgentStatus }) {
  const config = STATUS_CONFIG[status];
  return (
    <span className={cn("inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[11px] font-mono uppercase tracking-wide", config.className)}>
      {status === "running" && <span className="h-1.5 w-1.5 rounded-full bg-signal animate-blip" />}
      {config.label}
    </span>
  );
}
