import { z } from "zod";

// Document schemas
export const DocumentStatusSchema = z.enum([
  "pending",
  "processing",
  "ready",
  "error",
]);

export const DocumentSchema = z.object({
  id: z.string(),
  name: z.string(),
  status: DocumentStatusSchema,
  created_at: z.string(),
  updated_at: z.string().optional(),
  file_size: z.number().optional(),
  file_type: z.string().optional(),
});

export const DocumentListSchema = z.array(DocumentSchema);

export const UploadDocumentResponseSchema = z.object({
  id: z.string(),
  name: z.string(),
  status: DocumentStatusSchema,
  message: z.string().optional(),
});

export const DeleteDocumentResponseSchema = z.object({
  message: z.string(),
});

// Job schemas
export const JobStatusSchema = z.enum([
  "pending",
  "running",
  "completed",
  "failed",
]);

export const JobSchema = z.object({
  id: z.string(),
  status: JobStatusSchema,
  progress: z.number().optional(),
  message: z.string().optional(),
  result: z.unknown().optional(),
  error: z.string().optional(),
});

export const AnalyzeDocumentResponseSchema = z.object({
  job_id: z.string(),
  message: z.string().optional(),
});

// Chat schemas
export const ChatMessageRoleSchema = z.enum(["user", "assistant", "system"]);

export const ChatMessageSchema = z.object({
  role: ChatMessageRoleSchema,
  content: z.string(),
});

export const ChatRequestSchema = z.object({
  message: z.string(),
  document_ids: z.array(z.string()).optional(),
});

export const ChatResponseSchema = z.object({
  response: z.string(),
  sources: z.array(z.object({
    document_id: z.string(),
    document_name: z.string().optional(),
    chunk: z.string().optional(),
    score: z.number().optional(),
  })).optional(),
});

// Health schemas
export const HealthStatusSchema = z.object({
  status: z.string(),
  version: z.string().optional(),
  uptime: z.number().optional(),
  database: z.string().optional(),
  vector_store: z.string().optional(),
});

// API Error schema
export const ApiErrorSchema = z.object({
  detail: z.string().optional(),
  message: z.string().optional(),
});

// Type exports
export type Document = z.infer<typeof DocumentSchema>;
export type DocumentStatus = z.infer<typeof DocumentStatusSchema>;
export type DocumentList = z.infer<typeof DocumentListSchema>;
export type UploadDocumentResponse = z.infer<typeof UploadDocumentResponseSchema>;
export type DeleteDocumentResponse = z.infer<typeof DeleteDocumentResponseSchema>;
export type Job = z.infer<typeof JobSchema>;
export type JobStatus = z.infer<typeof JobStatusSchema>;
export type AnalyzeDocumentResponse = z.infer<typeof AnalyzeDocumentResponseSchema>;
export type ChatMessage = z.infer<typeof ChatMessageSchema>;
export type ChatMessageRole = z.infer<typeof ChatMessageRoleSchema>;
export type ChatRequest = z.infer<typeof ChatRequestSchema>;
export type ChatResponse = z.infer<typeof ChatResponseSchema>;
export type HealthStatus = z.infer<typeof HealthStatusSchema>;
export type ApiError = z.infer<typeof ApiErrorSchema>;
