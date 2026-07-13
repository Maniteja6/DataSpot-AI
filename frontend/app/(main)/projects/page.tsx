"use client";

import { useState } from "react";
import Link from "next/link";
import { FolderKanban, Plus } from "lucide-react";
import { useProjects, useCreateProject } from "@/features/projects/hooks/useProjects";
import { Card, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogTitle, DialogDescription, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { formatRelativeTime } from "@/lib/formatters";
import { EmptyState } from "@/components/shared/EmptyState";
import { TableSkeleton } from "@/components/skeletons/TableSkeleton";

export default function ProjectsPage() {
  const { data: projects, isLoading } = useProjects();
  const createProject = useCreateProject();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [open, setOpen] = useState(false);

  function handleCreate() {
    if (!name.trim()) return;
    createProject.mutate({ name, description });
    setName("");
    setDescription("");
    setOpen(false);
  }

  if (isLoading) return <TableSkeleton rows={4} />;

  return (
    <div className="space-y-6 animate-fade-up">
      <div className="flex justify-end">
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button size="sm"><Plus className="h-3.5 w-3.5" /> New Project</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogTitle>Create a project</DialogTitle>
            <DialogDescription>Group related datasets under one workspace.</DialogDescription>
            <div className="mt-4 space-y-3">
              <Input placeholder="Project name" value={name} onChange={(e) => setName(e.target.value)} />
              <Input placeholder="Short description" value={description} onChange={(e) => setDescription(e.target.value)} />
              <Button className="w-full" onClick={handleCreate}>Create project</Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {!projects || projects.length === 0 ? (
        <EmptyState icon={FolderKanban} title="No projects yet" description="Create a project to start organizing your datasets and analyses." />
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {projects.map((p) => (
            <Link key={p.id} href={`/projects/${p.id}`}>
              <Card className="scan-hover h-full">
                <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-signal-soft">
                  <FolderKanban className="h-4.5 w-4.5 text-signal" />
                </div>
                <CardTitle className="mb-1">{p.name}</CardTitle>
                <CardDescription>{p.description}</CardDescription>
                <div className="mt-4 flex items-center justify-between text-xs text-ink-faint">
                  <span>{p.datasetCount} datasets</span>
                  <span>Updated {formatRelativeTime(p.updatedAt)}</span>
                </div>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
