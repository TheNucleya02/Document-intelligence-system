import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { PageHeader } from "@/components/common/PageHeader";
import { ChatContainer } from "@/components/chat/ChatContainer";
import { useChat } from "@/hooks/useChat";

export default function Chat() {
  const { messages, sendMessage, clearMessages, isLoading } = useChat();

  return (
    <DashboardLayout>
      <PageHeader
        title="Chat"
        description="Ask questions about your documents"
      />
      <ChatContainer
        messages={messages}
        onSendMessage={sendMessage}
        onClearMessages={clearMessages}
        isLoading={isLoading}
      />
    </DashboardLayout>
  );
}
