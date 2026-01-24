import { useQuery } from "@tanstack/react-query";
import { getHealthStatus } from "@/api";

export function useHealthStatus() {
  return useQuery({
    queryKey: ["health"],
    queryFn: getHealthStatus,
    retry: 1,
    refetchInterval: 30000, // Check health every 30 seconds
  });
}
