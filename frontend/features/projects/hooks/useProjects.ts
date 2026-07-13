"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { projectsService } from "@/services/projects.service";
import { queryKeys } from "@/lib/react-query/queryKeys";

export function useProjects() {
  return useQuery({ queryKey: queryKeys.projects.all, queryFn: projectsService.list });
}

export function useCreateProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ name, description }: { name: string; description: string }) =>
      projectsService.create(name, description),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.projects.all }),
  });
}
