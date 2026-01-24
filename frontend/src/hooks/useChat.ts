import { useState, useCallback } from "react";
import { useMutation } from "@tanstack/react-query";
import { sendChatMessage } from "@/api";
import { type ChatMessage, type ChatResponse } from "@/types/api";
import { useToast } from "@/hooks/use-toast";

interface ChatHistoryEntry extends ChatMessage {
  id: string;
  sources?: ChatResponse["sources"];
  timestamp: Date;
}

export function useChat() {
  const [messages, setMessages] = useState<ChatHistoryEntry[]>([]);
  const { toast } = useToast();

  const mutation = useMutation({
    mutationFn: sendChatMessage,
    onError: (error) => {
      toast({
        title: "Chat error",
        description: error instanceof Error ? error.message : "Failed to send message",
        variant: "destructive",
      });
    },
  });

  const sendMessage = useCallback(async (content: string, documentIds?: string[]) => {
    // Add user message
    const userMessage: ChatHistoryEntry = {
      id: crypto.randomUUID(),
      role: "user",
      content,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);

    try {
      const response = await mutation.mutateAsync({
        message: content,
        document_ids: documentIds,
      });

      // Add assistant message
      const assistantMessage: ChatHistoryEntry = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: response.response,
        sources: response.sources,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);

      return response;
    } catch (error) {
      // Remove user message on error or add error indicator
      setMessages((prev) => prev.filter((m) => m.id !== userMessage.id));
      throw error;
    }
  }, [mutation]);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  return {
    messages,
    sendMessage,
    clearMessages,
    isLoading: mutation.isPending,
  };
}
