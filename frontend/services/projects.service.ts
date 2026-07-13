import { apiClient, withMockFallback } from "./api-client";
import { mockProjects } from "./mocks/mockData";
import type { Project } from "@/types/api.types";

export const projectsService = {
  list: () =>
    withMockFallback(
      () => apiClient.get<Project[]>("/api/v1/projects"),
      () => mockProjects
    ),
  create: (name: string, description: string) =>
    withMockFallback(
      () => apiClient.post<Project>("/api/v1/projects", { name, description }),
      () => ({
        id: `proj_${Date.now()}`,
        name,
        description,
        datasetCount: 0,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      })
    ),
};
