import { useState, useEffect, useCallback } from "react";
import { pollJobStatus } from "@/api";
import { type Job } from "@/types/api";
import { useToast } from "@/hooks/use-toast";
import { useQueryClient } from "@tanstack/react-query";

interface UseJobPollingOptions {
  onComplete?: (job: Job) => void;
  onError?: (error: Error) => void;
}

export function useJobPolling(options?: UseJobPollingOptions) {
  const [activeJobs, setActiveJobs] = useState<Map<string, Job>>(new Map());
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const startPolling = useCallback((jobId: string) => {
    // Add job to active jobs
    setActiveJobs((prev) => {
      const next = new Map(prev);
      next.set(jobId, {
        id: jobId,
        status: "pending",
      });
      return next;
    });

    const cancel = pollJobStatus(
      jobId,
      (job) => {
        // Update job status
        setActiveJobs((prev) => {
          const next = new Map(prev);
          next.set(jobId, job);
          return next;
        });
      },
      (job) => {
        // Job completed
        setActiveJobs((prev) => {
          const next = new Map(prev);
          next.set(jobId, job);
          return next;
        });

        // Invalidate documents to refresh status
        queryClient.invalidateQueries({ queryKey: ["documents"] });

        if (job.status === "completed") {
          toast({
            title: "Analysis complete",
            description: `Job ${jobId} has completed successfully.`,
          });
        } else if (job.status === "failed") {
          toast({
            title: "Analysis failed",
            description: job.error || `Job ${jobId} has failed.`,
            variant: "destructive",
          });
        }

        options?.onComplete?.(job);
      },
      (error) => {
        // Polling error
        setActiveJobs((prev) => {
          const next = new Map(prev);
          next.delete(jobId);
          return next;
        });

        toast({
          title: "Polling error",
          description: error.message,
          variant: "destructive",
        });

        options?.onError?.(error);
      }
    );

    return cancel;
  }, [toast, queryClient, options]);

  const clearJob = useCallback((jobId: string) => {
    setActiveJobs((prev) => {
      const next = new Map(prev);
      next.delete(jobId);
      return next;
    });
  }, []);

  return {
    activeJobs,
    startPolling,
    clearJob,
    isPolling: activeJobs.size > 0,
  };
}
