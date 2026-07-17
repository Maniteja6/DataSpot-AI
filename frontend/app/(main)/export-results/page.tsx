"use client";

import { FileText, Sheet as SheetIcon, FileSpreadsheet, FileJson, Presentation, Download } from "lucide-react";
import { useDatasets } from "@/features/datasets/hooks/useDatasets";
import { useExport } from "@/features/export/hooks/useExport";
import { Card, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/shared/EmptyState";
import type { ExportFormat } from "@/services/export.service";

const EXPORT_OPTIONS: { format: ExportFormat; label: string; description: string; icon: React.ElementType }[] = [
  { format: "pdf", label: "Executive Report (PDF)", description: "Findings, risks, and recommendations", icon: FileText },
  { format: "excel", label: "Excel Workbook", description: "Cleaned data, profiles, and model outputs", icon: FileSpreadsheet },
  { format: "csv", label: "CSV", description: "Cleaned dataset only", icon: SheetIcon },
  { format: "json", label: "JSON", description: "Full structured pipeline output", icon: FileJson },
  { format: "pptx", label: "PowerPoint Deck", description: "Executive-ready slide summary", icon: Presentation },
];

export default function ExportResultsPage() {
  const { data: datasets } = useDatasets();
  const datasetId = datasets?.[0]?.id ?? null;
  const exportMutation = useExport(datasetId ?? "");

  if (!datasetId) {
    return (
      <EmptyState
        icon={Download}
        title="No dataset yet"
        description="Upload a dataset from the Dashboard to export its results."
      />
    );
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 animate-fade-up">
      {EXPORT_OPTIONS.map(({ format, label, description, icon: Icon }) => (
        <Card key={format} className="flex flex-col justify-between">
          <div>
            <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-signal-soft">
              <Icon className="h-4.5 w-4.5 text-signal" />
            </div>
            <CardTitle className="mb-1">{label}</CardTitle>
            <CardDescription>{description}</CardDescription>
          </div>
          <Button
            className="mt-5"
            size="sm"
            variant="secondary"
            onClick={() => exportMutation.mutate(format)}
            disabled={exportMutation.isPending}
          >
            {exportMutation.isPending && exportMutation.variables === format ? "Preparing…" : "Export"}
          </Button>
        </Card>
      ))}
    </div>
  );
}
