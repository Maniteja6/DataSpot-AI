"use client";

import { useThemeStore } from "@/stores/useThemeStore";

export function useTheme() {
  return useThemeStore();
}
