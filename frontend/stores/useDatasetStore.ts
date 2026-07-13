import { create } from "zustand";
import type { Dataset } from "@/types/dataset.types";

interface DatasetState {
  datasets: Dataset[];
  upsertDataset: (dataset: Dataset) => void;
  removeDataset: (id: string) => void;
  setDatasets: (datasets: Dataset[]) => void;
}

export const useDatasetStore = create<DatasetState>((set) => ({
  datasets: [],
  upsertDataset: (dataset) =>
    set((state) => {
      const exists = state.datasets.some((d) => d.id === dataset.id);
      return {
        datasets: exists
          ? state.datasets.map((d) => (d.id === dataset.id ? dataset : d))
          : [dataset, ...state.datasets],
      };
    }),
  removeDataset: (id) =>
    set((state) => ({ datasets: state.datasets.filter((d) => d.id !== id) })),
  setDatasets: (datasets) => set({ datasets }),
}));
