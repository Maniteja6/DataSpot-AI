"use client";

import * as SwitchPrimitive from "@radix-ui/react-switch";
import { cn } from "@/utils/cn";

export function Switch({ className, ...props }: React.ComponentProps<typeof SwitchPrimitive.Root>) {
  return (
    <SwitchPrimitive.Root
      className={cn(
        "relative h-6 w-11 rounded-full bg-bg-raised border border-line data-[state=checked]:bg-signal-soft transition-colors",
        className
      )}
      {...props}
    >
      <SwitchPrimitive.Thumb className="block h-4 w-4 translate-x-1 rounded-full bg-ink-faint transition-transform data-[state=checked]:translate-x-6 data-[state=checked]:bg-signal" />
    </SwitchPrimitive.Root>
  );
}
