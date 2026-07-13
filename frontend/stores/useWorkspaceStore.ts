import { create } from "zustand";
import type { AgentActivity, PipelineStage } from "@/types/agent.types";

interface WorkspaceState {
  activeProjectId: string | null;
  activeDatasetId: string | null;
  pipelineStages: PipelineStage[];
  agentActivity: AgentActivity[];
  setActiveProject: (id: string | null) => void;
  setActiveDataset: (id: string | null) => void;
  setPipelineStages: (stages: PipelineStage[]) => void;
  setAgentActivity: (activity: AgentActivity[]) => void;
}

export const useWorkspaceStore = create<WorkspaceState>((set) => ({
  activeProjectId: null,
  activeDatasetId: null,
  pipelineStages: [],
  agentActivity: [],
  setActiveProject: (id) => set({ activeProjectId: id }),
  setActiveDataset: (id) => set({ activeDatasetId: id }),
  setPipelineStages: (stages) => set({ pipelineStages: stages }),
  setAgentActivity: (activity) => set({ agentActivity: activity }),
}));
