"use client";

import { ChevronDown, Database } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu";
import { useDatasets } from "@/features/datasets/hooks/useDatasets";

interface DatasetPickerProps {
  value: string | null;
  onChange: (datasetId: string) => void;
  onlyReady?: boolean;
  className?: string;
}

export function DatasetPicker({ value, onChange, onlyReady = true, className }: DatasetPickerProps) {
  const { data: datasets } = useDatasets();
  const options = (datasets ?? []).filter((d) => !onlyReady || d.status === "ready");
  const active = options.find((d) => d.id === value);

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="secondary" size="sm" className={className}>
          <Database className="h-3.5 w-3.5" />
          {active?.name ?? "Select a dataset"}
          <ChevronDown className="h-3.5 w-3.5" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start">
        {options.length === 0 ? (
          <DropdownMenuItem disabled>No ready datasets</DropdownMenuItem>
        ) : (
          options.map((d) => (
            <DropdownMenuItem key={d.id} onSelect={() => onChange(d.id)}>
              {d.name}
            </DropdownMenuItem>
          ))
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
