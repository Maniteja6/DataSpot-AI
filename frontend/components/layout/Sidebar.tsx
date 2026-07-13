"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Sparkles,
  TrendingUp,
  ShieldCheck,
  BrainCircuit,
  Target,
  Download,
  FolderKanban,
  Database,
  MessageCircle,
  Settings,
  UserCircle,
  ChevronsLeft,
  Plus,
} from "lucide-react";
import { cn } from "@/utils/cn";
import { useUiStore } from "@/stores/useUiStore";
import { NAV_ITEMS, NAV_FOOTER_ITEMS, APP_NAME, APP_TAGLINE } from "@/lib/constants";

const ICONS: Record<string, React.ElementType> = {
  LayoutDashboard,
  Sparkles,
  TrendingUp,
  ShieldCheck,
  BrainCircuit,
  Target,
  Download,
  FolderKanban,
  Database,
  MessageCircle,
  Settings,
  UserCircle,
};

function SpotMark({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 40 40" className={className} aria-hidden>
      <circle cx="20" cy="20" r="17" fill="none" stroke="rgb(var(--line))" strokeWidth="1.5" />
      <circle cx="20" cy="20" r="11" fill="none" stroke="rgb(var(--signal))" strokeOpacity="0.35" strokeWidth="1.5" />
      <circle cx="20" cy="20" r="3.4" fill="rgb(var(--signal))" />
      <g className="origin-center animate-sweep" style={{ transformOrigin: "20px 20px" }}>
        <path d="M20 20 L20 3" stroke="rgb(var(--signal))" strokeWidth="1.5" strokeLinecap="round" opacity="0.7" />
      </g>
    </svg>
  );
}

function NavLink({ href, label, icon }: { href: string; label: string; icon: string }) {
  const pathname = usePathname();
  const active = pathname === href || pathname.startsWith(`${href}/`);
  const Icon = ICONS[icon];
  const collapsed = useUiStore((s) => s.sidebarCollapsed);

  return (
    <Link
      href={href}
      className={cn(
        "group relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors",
        active
          ? "bg-signal-soft text-signal"
          : "text-ink-muted hover:bg-bg-raised hover:text-ink"
      )}
    >
      {active && (
        <span className="absolute left-0 top-1/2 h-5 w-[3px] -translate-y-1/2 rounded-full bg-signal" />
      )}
      <Icon className="h-[18px] w-[18px] shrink-0" />
      {!collapsed && <span className="truncate">{label}</span>}
    </Link>
  );
}

export function Sidebar() {
  const { sidebarCollapsed, toggleSidebar } = useUiStore();

  return (
    <aside
      className={cn(
        "sticky top-0 flex h-screen shrink-0 flex-col border-r border-line bg-bg-surface/60 backdrop-blur-xl transition-[width] duration-300",
        sidebarCollapsed ? "w-[76px]" : "w-[264px]"
      )}
    >
      <div className="flex items-center justify-between px-4 py-5">
        <div className="flex items-center gap-2.5 overflow-hidden">
          <SpotMark className="h-8 w-8 shrink-0" />
          {!sidebarCollapsed && (
            <div className="min-w-0">
              <p className="font-display text-[15px] font-semibold leading-tight text-ink">
                {APP_NAME}
              </p>
              <p className="truncate text-[11px] text-ink-faint">{APP_TAGLINE}</p>
            </div>
          )}
        </div>
        <button
          onClick={toggleSidebar}
          className="text-ink-faint hover:text-signal"
          aria-label="Collapse sidebar"
        >
          <ChevronsLeft
            className={cn("h-4 w-4 transition-transform", sidebarCollapsed && "rotate-180")}
          />
        </button>
      </div>

      <div className="px-3">
        <Link
          href="/datasets"
          className="flex w-full items-center justify-center gap-2 rounded-xl bg-signal px-3 py-2.5 text-sm font-medium text-[#04140f] transition-transform hover:scale-[1.02]"
        >
          <Plus className="h-4 w-4" />
          {!sidebarCollapsed && "New Project"}
        </Link>
      </div>

      <nav className="mt-6 flex-1 space-y-1 overflow-y-auto px-3">
        {NAV_ITEMS.map((item) => (
          <NavLink key={item.href} {...item} />
        ))}
      </nav>

      <div className="space-y-1 border-t border-line px-3 py-4">
        {NAV_FOOTER_ITEMS.map((item) => (
          <NavLink key={item.href} {...item} />
        ))}
      </div>
    </aside>
  );
}
