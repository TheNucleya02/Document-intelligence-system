import { apiGet, apiPost, apiPostFormData, apiDelete } from "./client";
import {
  DocumentListSchema,
  UploadDocumentResponseSchema,
  DeleteDocumentResponseSchema,
  AnalyzeDocumentResponseSchema,
  type Document,
  type UploadDocumentResponse,
  type DeleteDocumentResponse,
  type AnalyzeDocumentResponse,
} from "@/types/api";

export async function getDocuments(): Promise<Document[]> {
  return apiGet("/documents", DocumentListSchema);
}

export async function uploadDocument(file: File): Promise<UploadDocumentResponse> {
  const formData = new FormData();
  formData.append("file", file);
  
  return apiPostFormData("/documents", formData, UploadDocumentResponseSchema);
}

export async function deleteDocument(documentId: string): Promise<DeleteDocumentResponse> {
  return apiDelete(`/documents/${documentId}`, DeleteDocumentResponseSchema);
}

export async function analyzeDocument(documentId: string): Promise<AnalyzeDocumentResponse> {
  return apiPost(`/documents/${documentId}/analyze`, undefined, AnalyzeDocumentResponseSchema);
}
