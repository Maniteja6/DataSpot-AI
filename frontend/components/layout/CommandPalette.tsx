"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Search } from "lucide-react";
import { VisuallyHidden } from "@radix-ui/react-visually-hidden";
import { Dialog, DialogContent, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { useUiStore } from "@/stores/useUiStore";
import { NAV_ITEMS } from "@/lib/constants";

export function CommandPalette() {
  const { commandPaletteOpen, setCommandPaletteOpen } = useUiStore();
  const [query, setQuery] = useState("");
  const router = useRouter();

  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setCommandPaletteOpen(!commandPaletteOpen);
      }
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [commandPaletteOpen, setCommandPaletteOpen]);

  const filtered = NAV_ITEMS.filter((i) =>
    i.label.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <Dialog open={commandPaletteOpen} onOpenChange={setCommandPaletteOpen}>
      <DialogContent className="top-[20%] max-w-md translate-y-0 p-0">
        <VisuallyHidden asChild>
          <DialogTitle>Command palette</DialogTitle>
        </VisuallyHidden>
        <VisuallyHidden asChild>
          <DialogDescription>Search and jump to a page</DialogDescription>
        </VisuallyHidden>
        <div className="flex items-center gap-2 border-b border-line px-4 py-3">
          <Search className="h-4 w-4 text-ink-faint" />
          <input
            autoFocus
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Jump to a page…"
            className="w-full bg-transparent text-sm text-ink placeholder:text-ink-faint focus:outline-none"
          />
        </div>
        <div className="max-h-72 overflow-y-auto p-2">
          {filtered.map((item) => (
            <button
              key={item.href}
              onClick={() => {
                router.push(item.href);
                setCommandPaletteOpen(false);
                setQuery("");
              }}
              className="flex w-full items-center rounded-lg px-3 py-2 text-left text-sm text-ink-muted hover:bg-signal-soft hover:text-signal"
            >
              {item.label}
            </button>
          ))}
          {filtered.length === 0 && (
            <p className="px-3 py-4 text-center text-xs text-ink-faint">No matches.</p>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
