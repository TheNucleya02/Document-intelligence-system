import { z } from "zod";

// --------------------
// Documents
// --------------------

export const DocumentStatusSchema = z.enum([
  "uploaded",
  "processing",
  "ready",
  "error",
]);

export const DocumentSchema = z.object({
  id: z.string(),
  filename: z.string(),
  status: DocumentStatusSchema,
  created_at: z.string(),
});

export const DocumentListSchema = z.array(DocumentSchema);

// Upload response

export const UploadItemSchema = z.object({
  document_id: z.string(),
  job_id: z.string(),
  filename: z.string(),
});

export const UploadDocumentResponseSchema = z.object({
  message: z.string(),
  items: z.array(UploadItemSchema),
});

// Delete response

export const DeleteDocumentResponseSchema = z.object({
  message: z.string(),
});

// --------------------
// Jobs
// --------------------

export const JobStatusSchema = z.enum([
  "pending",
  "running",
  "completed",
  "failed",
]);

export const JobSchema = z.object({
  status: JobStatusSchema,
  message: z.string().optional(),
});

// --------------------
// Analyze
// --------------------

export const AnalyzeDocumentResponseSchema = z.unknown(); 
// Your backend returns arbitrary analysis JSON

// --------------------
// Chat
// --------------------

export const ChatResponseSchema = z.object({
  answer: z.string(),
  sources: z.array(z.string()),
});

// --------------------
// Health
// --------------------

export const HealthStatusSchema = z.object({
  status: z.string(),
  timestamp: z.number(),
});

// --------------------
// Types
// --------------------

export type Document = z.infer<typeof DocumentSchema>;
export type DocumentStatus = z.infer<typeof DocumentStatusSchema>;
export type DocumentList = z.infer<typeof DocumentListSchema>;
export type UploadDocumentResponse = z.infer<typeof UploadDocumentResponseSchema>;
export type DeleteDocumentResponse = z.infer<typeof DeleteDocumentResponseSchema>;
export type Job = z.infer<typeof JobSchema>;
export type JobStatus = z.infer<typeof JobStatusSchema>;
export type AnalyzeDocumentResponse = z.infer<typeof AnalyzeDocumentResponseSchema>;
export type ChatResponse = z.infer<typeof ChatResponseSchema>;
export type HealthStatus = z.infer<typeof HealthStatusSchema>;
