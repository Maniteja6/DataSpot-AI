"use client";

import { useState } from "react";
import { Send } from "lucide-react";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";

const MIN_LENGTH = 10;

export function BusinessRequirementForm({
  onSubmit,
  isPending,
}: {
  onSubmit: (requirement: string) => void;
  isPending: boolean;
}) {
  const [text, setText] = useState("");

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        if (text.trim().length >= MIN_LENGTH) onSubmit(text.trim());
      }}
      className="space-y-3"
    >
      <Textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder='Describe a business goal, e.g. "increase Q4 revenue by 15%" or "reduce customer churn"'
        disabled={isPending}
      />
      <div className="flex items-center justify-between">
        <p className="text-xs text-ink-faint">
          {text.trim().length < MIN_LENGTH
            ? `At least ${MIN_LENGTH} characters`
            : "Grounded in this dataset's analytics"}
        </p>
        <Button type="submit" size="sm" disabled={isPending || text.trim().length < MIN_LENGTH}>
          <Send className="h-3.5 w-3.5" />
          {isPending ? "Generating…" : "Generate recommendations"}
        </Button>
      </div>
    </form>
  );
}
