"use client";

import { useMemo } from "react";
import { AgGridReact } from "ag-grid-react";
import type { ColDef } from "ag-grid-community";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-quartz.css";

interface AgGridTableProps<T extends object> {
  rows: T[];
  columns: ColDef<T>[];
  height?: number;
}

export function AgGridTable<T extends object>({ rows, columns, height = 420 }: AgGridTableProps<T>) {
  const defaultColDef = useMemo<ColDef>(
    () => ({ sortable: true, filter: true, resizable: true, flex: 1, minWidth: 110 }),
    []
  );

  return (
    <div
      className="ag-theme-quartz-dark dataspot-grid rounded-xl overflow-hidden border border-line"
      style={{ height }}
    >
      <AgGridReact<T>
        rowData={rows}
        columnDefs={columns}
        defaultColDef={defaultColDef}
        animateRows
        rowHeight={38}
        headerHeight={38}
      />
      <style jsx global>{`
        .dataspot-grid {
          --ag-background-color: rgb(var(--bg-surface));
          --ag-header-background-color: rgb(var(--bg-raised));
          --ag-odd-row-background-color: transparent;
          --ag-border-color: rgb(var(--line));
          --ag-header-foreground-color: rgb(var(--ink-faint));
          --ag-foreground-color: rgb(var(--ink-muted));
          --ag-font-size: 12.5px;
          --ag-row-hover-color: var(--signal-soft);
        }
      `}</style>
    </div>
  );
}
