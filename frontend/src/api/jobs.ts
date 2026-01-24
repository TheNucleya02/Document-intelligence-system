import { apiGet } from "./client";
import { JobSchema, type Job } from "@/types/api";

export async function getJobStatus(jobId: string): Promise<Job> {
  return apiGet(`/jobs/${jobId}`, JobSchema);
}

export function pollJobStatus(
  jobId: string,
  onUpdate: (job: Job) => void,
  onComplete: (job: Job) => void,
  onError: (error: Error) => void,
  intervalMs: number = 2000
): () => void {
  let isCancelled = false;

  const poll = async () => {
    if (isCancelled) return;

    try {
      const job = await getJobStatus(jobId);
      onUpdate(job);

      if (job.status === "completed" || job.status === "failed") {
        onComplete(job);
        return;
      }

      // Continue polling
      setTimeout(poll, intervalMs);
    } catch (error) {
      if (!isCancelled) {
        onError(error instanceof Error ? error : new Error("Unknown error"));
      }
    }
  };

  // Start polling
  poll();

  // Return cancel function
  return () => {
    isCancelled = true;
  };
}
