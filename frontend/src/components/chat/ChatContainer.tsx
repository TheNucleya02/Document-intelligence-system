import { useEffect, useRef } from "react";
import { MessageSquare, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ChatMessage } from "./ChatMessage";
import { ChatInput } from "./ChatInput";
import { type ChatMessage as ChatMessageType, type ChatResponse } from "@/types/api";

interface ChatHistoryEntry extends ChatMessageType {
  id: string;
  sources?: ChatResponse["sources"];
  timestamp: Date;
}

interface ChatContainerProps {
  messages: ChatHistoryEntry[];
  onSendMessage: (message: string) => void;
  onClearMessages: () => void;
  isLoading: boolean;
}

export function ChatContainer({
  messages,
  onSendMessage,
  onClearMessages,
  isLoading,
}: ChatContainerProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="flex flex-col h-[calc(100vh-theme(spacing.32))] bg-card border rounded-lg">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b">
        <div className="flex items-center gap-2">
          <MessageSquare className="h-5 w-5 text-muted-foreground" />
          <h2 className="font-medium">Document Q&A</h2>
        </div>
        {messages.length > 0 && (
          <Button variant="ghost" size="sm" onClick={onClearMessages}>
            <Trash2 className="h-4 w-4 mr-1" />
            Clear
          </Button>
        )}
      </div>

      {/* Messages */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="h-16 w-16 rounded-full bg-muted flex items-center justify-center mb-4">
              <MessageSquare className="h-8 w-8 text-muted-foreground" />
            </div>
            <h3 className="text-lg font-medium mb-1">Start a conversation</h3>
            <p className="text-muted-foreground text-sm max-w-sm">
              Ask questions about your uploaded documents. The AI will search through
              your documents to find relevant answers.
            </p>
          </div>
        ) : (
          messages.map((msg) => <ChatMessage key={msg.id} message={msg} />)
        )}

        {/* Loading indicator */}
        {isLoading && (
          <div className="flex gap-3 animate-slide-in">
            <div className="h-8 w-8 rounded-full bg-muted flex items-center justify-center">
              <div className="h-4 w-4 rounded-full bg-muted-foreground/30 animate-pulse-subtle" />
            </div>
            <div className="bg-muted rounded-2xl rounded-tl-sm px-4 py-3">
              <div className="flex gap-1">
                <div className="h-2 w-2 rounded-full bg-muted-foreground/40 animate-bounce" style={{ animationDelay: "0ms" }} />
                <div className="h-2 w-2 rounded-full bg-muted-foreground/40 animate-bounce" style={{ animationDelay: "150ms" }} />
                <div className="h-2 w-2 rounded-full bg-muted-foreground/40 animate-bounce" style={{ animationDelay: "300ms" }} />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="p-4 border-t">
        <ChatInput onSend={onSendMessage} isLoading={isLoading} />
      </div>
    </div>
  );
}
