import { RefreshCw } from "lucide-react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { PageHeader } from "@/components/common/PageHeader";
import { StatusCard } from "@/components/status/StatusCard";
import { Button } from "@/components/ui/button";
import { useHealthStatus } from "@/hooks/useHealthStatus";
import { API_BASE_URL } from "@/api";

export default function Status() {
  const { data, isLoading, isError, refetch, dataUpdatedAt } = useHealthStatus();

  const getApiStatus = (): "healthy" | "unhealthy" | "loading" => {
    if (isLoading) return "loading";
    if (isError) return "unhealthy";
    return data?.status === "ok" || data?.status === "healthy" ? "healthy" : "unhealthy";
  };

  const lastChecked = dataUpdatedAt
    ? new Date(dataUpdatedAt).toLocaleTimeString("en-US", {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      })
    : "Never";

  return (
    <DashboardLayout>
      <PageHeader
        title="System Status"
        description="Monitor the health of backend services"
        actions={
          <Button variant="outline" onClick={() => refetch()} disabled={isLoading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
        }
      />

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <StatusCard
          title="API Server"
          status={getApiStatus()}
          description="Main backend API service"
          details={{
            endpoint: API_BASE_URL,
            version: data?.version,
            uptime: data?.uptime ? `${Math.round(data.uptime / 60)} min` : undefined,
          }}
        />

        <StatusCard
          title="Database"
          status={
            isLoading
              ? "loading"
              : data?.database === "connected"
              ? "healthy"
              : isError
              ? "unhealthy"
              : "unknown"
          }
          description="Document storage database"
          details={{
            status: data?.database || (isError ? "unreachable" : "unknown"),
          }}
        />

        <StatusCard
          title="Vector Store"
          status={
            isLoading
              ? "loading"
              : data?.vector_store === "connected"
              ? "healthy"
              : isError
              ? "unhealthy"
              : "unknown"
          }
          description="RAG vector database"
          details={{
            status: data?.vector_store || (isError ? "unreachable" : "unknown"),
          }}
        />
      </div>

      <div className="mt-6 text-sm text-muted-foreground">
        Last checked: {lastChecked}
      </div>
    </DashboardLayout>
  );
}
