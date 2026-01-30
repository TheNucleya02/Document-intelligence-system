import { useState } from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { PageHeader } from "@/components/common/PageHeader";
import { LoadingState } from "@/components/common/LoadingState";
import { ErrorState } from "@/components/common/ErrorState";
import { DocumentList } from "@/components/documents/DocumentList";
import { DocumentUpload } from "@/components/documents/DocumentUpload";
import { JobStatusBadge } from "@/components/documents/JobStatusBadge";
import {
  useDocuments,
  useUploadDocument,
  useDeleteDocument,
  useAnalyzeDocument,
} from "@/hooks/useDocuments";
import { useJobPolling } from "@/hooks/useJobPolling";

export default function Documents() {
  const { data: documents, isLoading, isError, error, refetch } = useDocuments();
  const uploadMutation = useUploadDocument();
  const deleteMutation = useDeleteDocument();
  const analyzeMutation = useAnalyzeDocument();
  const { activeJobs, startPolling, clearJob } = useJobPolling();
  const [analyzingDocumentId, setAnalyzingDocumentId] = useState<string>();

  const handleUpload = async (file: File) => {
    const res = await uploadMutation.mutateAsync(file);

    // Start polling job for first uploaded file
    const item = res.items[0];
    if (item?.job_id) {
      startPolling(item.job_id);
    }

    // Refresh documents list
    refetch();
  };


  const handleDelete = (documentId: string) => {
    deleteMutation.mutate(documentId);
  };

  const handleAnalyze = async (documentId: string) => {
    setAnalyzingDocumentId(documentId);
    try {
      const result = await analyzeMutation.mutateAsync(documentId);
      startPolling(result.job_id);
    } finally {
      setAnalyzingDocumentId(undefined);
    }
  };

  return (
    <DashboardLayout>
      <PageHeader
        title="Documents"
        description="Upload and manage your documents for analysis"
        actions={
          <DocumentUpload
            onUpload={handleUpload}
            isUploading={uploadMutation.isPending}
          />
        }
      />

      {/* Active Jobs */}
      {activeJobs.size > 0 && (
        <div className="space-y-2 mb-6">
          {Array.from(activeJobs.entries()).map(([jobId, job]) => (
            <JobStatusBadge
              key={jobId}
              job={job}
              onDismiss={() => clearJob(jobId)}
            />
          ))}
        </div>
      )}

      {/* Content */}
      {isLoading ? (
        <LoadingState message="Loading documents..." />
      ) : isError ? (
        <ErrorState
          title="Failed to load documents"
          message={error instanceof Error ? error.message : "An error occurred"}
          onRetry={() => refetch()}
        />
      ) : (
        <DocumentList
          documents={documents || []}
          onDelete={handleDelete}
          onAnalyze={handleAnalyze}
          isDeleting={deleteMutation.isPending}
          isAnalyzing={analyzeMutation.isPending}
          analyzingDocumentId={analyzingDocumentId}
        />
      )}
    </DashboardLayout>
  );
}
