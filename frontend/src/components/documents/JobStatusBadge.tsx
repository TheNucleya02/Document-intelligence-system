import { Loader2, CheckCircle, XCircle, Clock } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { type Job } from "@/types/api";

interface JobStatusBadgeProps {
  job: Job;
  onDismiss?: () => void;
}

const statusConfig = {
  pending: {
    icon: Clock,
    label: "Pending",
    variant: "secondary" as const,
    animate: false,
  },
  running: {
    icon: Loader2,
    label: "Running",
    variant: "default" as const,
    animate: true,
  },
  completed: {
    icon: CheckCircle,
    label: "Completed",
    variant: "outline" as const,
    animate: false,
  },
  failed: {
    icon: XCircle,
    label: "Failed",
    variant: "destructive" as const,
    animate: false,
  },
};

export function JobStatusBadge({ job, onDismiss }: JobStatusBadgeProps) {
  const config = statusConfig[job.status];
  const Icon = config.icon;

  return (
    <div className="flex items-center gap-2 p-3 bg-card border rounded-lg animate-fade-in">
      <Badge variant={config.variant} className="font-normal">
        <Icon className={`h-3 w-3 mr-1 ${config.animate ? "animate-spin" : ""}`} />
        {config.label}
      </Badge>
      <span className="text-sm text-muted-foreground">
        Job: {job.id.slice(0, 8)}...
      </span>
      {job.progress !== undefined && job.status === "running" && (
        <span className="text-sm font-medium">{job.progress}%</span>
      )}
      {job.message && (
        <span className="text-sm text-muted-foreground">{job.message}</span>
      )}
      {(job.status === "completed" || job.status === "failed") && onDismiss && (
        <button
          onClick={onDismiss}
          className="text-xs text-muted-foreground hover:text-foreground ml-auto"
        >
          Dismiss
        </button>
      )}
    </div>
  );
}
