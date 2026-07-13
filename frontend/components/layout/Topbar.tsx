"use client";

import { usePathname } from "next/navigation";
import { Search, Bell } from "lucide-react";
import { ThemeToggle } from "./ThemeToggle";
import { useUiStore } from "@/stores/useUiStore";
import { NAV_ITEMS, NAV_FOOTER_ITEMS } from "@/lib/constants";

function currentLabel(pathname: string) {
  const all = [...NAV_ITEMS, ...NAV_FOOTER_ITEMS];
  const match = all.find((i) => pathname === i.href || pathname.startsWith(`${i.href}/`));
  return match?.label ?? "Dashboard";
}

export function Topbar() {
  const pathname = usePathname();
  const setCommandPaletteOpen = useUiStore((s) => s.setCommandPaletteOpen);

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-line bg-bg/80 px-6 backdrop-blur-xl">
      <div>
        <p className="eyebrow">Workspace</p>
        <h1 className="font-display text-lg font-medium text-ink">{currentLabel(pathname)}</h1>
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={() => setCommandPaletteOpen(true)}
          className="flex items-center gap-2 rounded-xl border border-line bg-bg-surface/60 px-3 py-2 text-xs text-ink-faint transition-colors hover:border-signal/40 hover:text-ink"
        >
          <Search className="h-3.5 w-3.5" />
          Search
          <kbd className="ml-2 rounded border border-line px-1.5 py-0.5 font-mono text-[10px]">⌘K</kbd>
        </button>
        <button className="relative rounded-xl p-2 text-ink-faint hover:text-ink">
          <Bell className="h-4 w-4" />
          <span className="absolute right-1.5 top-1.5 h-1.5 w-1.5 rounded-full bg-signal animate-blip" />
        </button>
        <ThemeToggle />
        <div className="h-8 w-8 rounded-full bg-gradient-to-br from-signal/60 to-bg-raised" />
      </div>
    </header>
  );
}
