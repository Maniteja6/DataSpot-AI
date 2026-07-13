import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/utils/cn";

const badgeVariants = cva(
  "inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[11px] font-medium font-mono uppercase tracking-wide",
  {
    variants: {
      variant: {
        signal: "bg-signal-soft text-signal",
        amber: "bg-amber/15 text-amber",
        rose: "bg-rose/15 text-rose",
        neutral: "bg-bg-raised text-ink-muted border border-line",
      },
    },
    defaultVariants: { variant: "neutral" },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return <span className={cn(badgeVariants({ variant, className }))} {...props} />;
}
