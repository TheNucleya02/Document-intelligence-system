import { apiPost } from "./client";
import {
  ChatResponseSchema,
  type ChatRequest,
  type ChatResponse,
} from "@/types/api";

export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  return apiPost("/chat", request, ChatResponseSchema);
}
