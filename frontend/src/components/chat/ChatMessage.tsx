import { User, Bot, FileText } from "lucide-react";
import { type ChatMessage as ChatMessageType, type ChatResponse } from "@/types/api";

interface ChatMessageProps {
  message: ChatMessageType & {
    id: string;
    sources?: ChatResponse["sources"];
    timestamp: Date;
  };
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={`flex gap-3 ${isUser ? "flex-row-reverse" : ""} animate-slide-in`}
    >
      {/* Avatar */}
      <div
        className={`
          h-8 w-8 rounded-full flex items-center justify-center shrink-0
          ${isUser ? "bg-primary" : "bg-muted"}
        `}
      >
        {isUser ? (
          <User className="h-4 w-4 text-primary-foreground" />
        ) : (
          <Bot className="h-4 w-4 text-muted-foreground" />
        )}
      </div>

      {/* Content */}
      <div className={`flex flex-col gap-2 max-w-[80%] ${isUser ? "items-end" : ""}`}>
        <div
          className={`
            px-4 py-3 rounded-2xl text-sm
            ${isUser 
              ? "bg-primary text-primary-foreground rounded-tr-sm" 
              : "bg-muted rounded-tl-sm"
            }
          `}
        >
          <p className="whitespace-pre-wrap">{message.content}</p>
        </div>

        {/* Sources */}
        {message.sources && message.sources.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {message.sources.map((source, index) => (
              <div
                key={index}
                className="flex items-center gap-1 px-2 py-1 bg-secondary rounded text-xs text-muted-foreground"
              >
                <FileText className="h-3 w-3" />
                <span>{source.document_name || source.document_id.slice(0, 8)}</span>
                {source.score && (
                  <span className="text-[10px] opacity-60">
                    ({Math.round(source.score * 100)}%)
                  </span>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Timestamp */}
        <span className="text-[10px] text-muted-foreground px-1">
          {message.timestamp.toLocaleTimeString("en-US", {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </span>
      </div>
    </div>
  );
}
