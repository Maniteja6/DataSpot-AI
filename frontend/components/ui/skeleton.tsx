import { cn } from "@/utils/cn";

export function Skeleton({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("animate-pulse rounded-lg bg-bg-raised/80", className)}
      {...props}
    />
  );
}
