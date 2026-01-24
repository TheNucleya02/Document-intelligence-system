import { CheckCircle, XCircle, AlertCircle, Loader2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface StatusCardProps {
  title: string;
  status: "healthy" | "unhealthy" | "unknown" | "loading";
  details?: Record<string, string | number | boolean | undefined>;
  description?: string;
}

const statusConfig = {
  healthy: {
    icon: CheckCircle,
    label: "Healthy",
    variant: "outline" as const,
    color: "text-success",
  },
  unhealthy: {
    icon: XCircle,
    label: "Unhealthy",
    variant: "destructive" as const,
    color: "text-destructive",
  },
  unknown: {
    icon: AlertCircle,
    label: "Unknown",
    variant: "secondary" as const,
    color: "text-warning",
  },
  loading: {
    icon: Loader2,
    label: "Checking...",
    variant: "secondary" as const,
    color: "text-muted-foreground",
  },
};

export function StatusCard({ title, status, details, description }: StatusCardProps) {
  const config = statusConfig[status];
  const Icon = config.icon;

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base font-medium">{title}</CardTitle>
          <Badge variant={config.variant} className="font-normal">
            <Icon
              className={`h-3 w-3 mr-1 ${config.color} ${
                status === "loading" ? "animate-spin" : ""
              }`}
            />
            {config.label}
          </Badge>
        </div>
        {description && (
          <p className="text-sm text-muted-foreground">{description}</p>
        )}
      </CardHeader>
      {details && Object.keys(details).length > 0 && (
        <CardContent className="pt-0">
          <dl className="grid grid-cols-2 gap-2 text-sm">
            {Object.entries(details).map(([key, value]) => (
              <div key={key} className="space-y-0.5">
                <dt className="text-muted-foreground capitalize">
                  {key.replace(/_/g, " ")}
                </dt>
                <dd className="font-medium">
                  {value === undefined ? "—" : String(value)}
                </dd>
              </div>
            ))}
          </dl>
        </CardContent>
      )}
    </Card>
  );
}
