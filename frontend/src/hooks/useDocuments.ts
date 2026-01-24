import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getDocuments, uploadDocument, deleteDocument, analyzeDocument } from "@/api";
import { useToast } from "@/hooks/use-toast";

export function useDocuments() {
  const { toast } = useToast();

  return useQuery({
    queryKey: ["documents"],
    queryFn: getDocuments,
    retry: 1,
    refetchInterval: 10000, // Refetch every 10 seconds to catch status changes
  });
}

export function useUploadDocument() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: uploadDocument,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
      toast({
        title: "Document uploaded",
        description: `${data.name} has been uploaded successfully.`,
      });
    },
    onError: (error) => {
      toast({
        title: "Upload failed",
        description: error instanceof Error ? error.message : "Failed to upload document",
        variant: "destructive",
      });
    },
  });
}

export function useDeleteDocument() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: deleteDocument,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
      toast({
        title: "Document deleted",
        description: "The document has been deleted.",
      });
    },
    onError: (error) => {
      toast({
        title: "Delete failed",
        description: error instanceof Error ? error.message : "Failed to delete document",
        variant: "destructive",
      });
    },
  });
}

export function useAnalyzeDocument() {
  const { toast } = useToast();

  return useMutation({
    mutationFn: analyzeDocument,
    onSuccess: (data) => {
      toast({
        title: "Analysis started",
        description: `Job ID: ${data.job_id}`,
      });
    },
    onError: (error) => {
      toast({
        title: "Analysis failed",
        description: error instanceof Error ? error.message : "Failed to start analysis",
        variant: "destructive",
      });
    },
  });
}
