import { apiGet } from "./client";
import { HealthStatusSchema, type HealthStatus } from "@/types/api";

export async function getHealthStatus(): Promise<HealthStatus> {
  return apiGet("/health", HealthStatusSchema);
}
