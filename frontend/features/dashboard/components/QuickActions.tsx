import Link from "next/link";
import { Sparkles, TrendingUp, Target, Download } from "lucide-react";

const ACTIONS = [
  { href: "/data-insights", label: "Explore insights", icon: Sparkles },
  { href: "/predictive-analysis", label: "Run forecast", icon: TrendingUp },
  { href: "/decision-making", label: "View decisions", icon: Target },
  { href: "/export-results", label: "Export report", icon: Download },
];

export function QuickActions() {
  return (
    <div className="grid grid-cols-2 gap-3">
      {ACTIONS.map(({ href, label, icon: Icon }) => (
        <Link
          key={href}
          href={href}
          className="scan-hover flex flex-col items-start gap-2 rounded-xl border border-line bg-bg-surface/50 p-3 transition-colors hover:border-signal/40"
        >
          <Icon className="h-4 w-4 text-signal" />
          <span className="text-xs font-medium text-ink">{label}</span>
        </Link>
      ))}
    </div>
  );
}
