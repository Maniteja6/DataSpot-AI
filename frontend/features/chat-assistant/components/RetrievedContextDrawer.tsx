"use client";

import { useState } from "react";
import { ChevronDown } from "lucide-react";
import { cn } from "@/utils/cn";
import { CitationSourceCard } from "./CitationSourceCard";
import type { CitationSource } from "@/types/rag.types";

export function RetrievedContextDrawer({ citations }: { citations: CitationSource[] }) {
  const [open, setOpen] = useState(false);
  if (citations.length === 0) return null;

  return (
    <div className="mt-2">
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex items-center gap-1.5 text-[11px] font-mono uppercase tracking-wide text-ink-faint hover:text-signal"
      >
        <ChevronDown className={cn("h-3 w-3 transition-transform", open && "rotate-180")} />
        {citations.length} source{citations.length > 1 ? "s" : ""} used
      </button>
      {open && (
        <div className="mt-2 grid gap-2 sm:grid-cols-2">
          {citations.map((c) => (
            <CitationSourceCard key={c.id} source={c} />
          ))}
        </div>
      )}
    </div>
  );
}
