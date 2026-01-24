import { z } from "zod";
import { ApiErrorSchema } from "@/types/api";

// Get API base URL from environment or use default
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public detail?: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

interface RequestOptions extends RequestInit {
  params?: Record<string, string>;
}

async function handleResponse<T>(
  response: Response,
  schema?: z.ZodSchema<T>
): Promise<T> {
  if (!response.ok) {
    let errorMessage = `Request failed with status ${response.status}`;
    let detail: string | undefined;

    try {
      const errorBody = await response.json();
      const parsed = ApiErrorSchema.safeParse(errorBody);
      if (parsed.success) {
        detail = parsed.data.detail || parsed.data.message;
        errorMessage = detail || errorMessage;
      }
    } catch {
      // Response body might not be JSON
    }

    throw new ApiError(errorMessage, response.status, detail);
  }

  // Handle empty responses (204 No Content, etc.)
  const contentType = response.headers.get("content-type");
  if (!contentType || !contentType.includes("application/json")) {
    return {} as T;
  }

  const data = await response.json();

  if (schema) {
    const result = schema.safeParse(data);
    if (!result.success) {
      console.error("API response validation failed:", result.error);
      // Return data anyway but log the validation error
      return data as T;
    }
    return result.data;
  }

  return data as T;
}

export async function apiGet<T>(
  endpoint: string,
  schema?: z.ZodSchema<T>,
  options?: RequestOptions
): Promise<T> {
  const url = new URL(`${API_BASE_URL}${endpoint}`);
  
  if (options?.params) {
    Object.entries(options.params).forEach(([key, value]) => {
      url.searchParams.append(key, value);
    });
  }

  const response = await fetch(url.toString(), {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  return handleResponse(response, schema);
}

export async function apiPost<T, D = unknown>(
  endpoint: string,
  data?: D,
  schema?: z.ZodSchema<T>,
  options?: RequestOptions
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    body: data ? JSON.stringify(data) : undefined,
    ...options,
  });

  return handleResponse(response, schema);
}

export async function apiPostFormData<T>(
  endpoint: string,
  formData: FormData,
  schema?: z.ZodSchema<T>,
  options?: RequestOptions
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const response = await fetch(url, {
    method: "POST",
    // Don't set Content-Type for FormData, browser will set it with boundary
    ...options,
    body: formData,
  });

  return handleResponse(response, schema);
}

export async function apiDelete<T>(
  endpoint: string,
  schema?: z.ZodSchema<T>,
  options?: RequestOptions
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const response = await fetch(url, {
    method: "DELETE",
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  return handleResponse(response, schema);
}

export { API_BASE_URL };
