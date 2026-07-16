import * as React from "react";
import { cn } from "@/utils/cn";

export const Textarea = React.forwardRef<HTMLTextAreaElement, React.TextareaHTMLAttributes<HTMLTextAreaElement>>(
  ({ className, ...props }, ref) => (
    <textarea
      ref={ref}
      className={cn(
        "min-h-[96px] w-full resize-none rounded-xl border border-line bg-bg-surface px-3 py-2 text-sm text-ink placeholder:text-ink-faint focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-signal/50",
        className
      )}
      {...props}
    />
  )
);
Textarea.displayName = "Textarea";
