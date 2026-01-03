import { useState } from "react";
import { useChat } from "@/hooks/useChat";
import { useTheme } from "@/hooks/useTheme";
import {
  ChatSidebar,
  ChatHeader,
  ChatMessages,
  ChatInput,
} from "@/components/chat";

const Index = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const { theme, setTheme } = useTheme();

  const {
    activeChat,
    activeChatId,
    groupedChats,
    isStreaming,
    setActiveChatId,
    createNewChat,
    deleteChat,
    renameChat,
    sendMessage,
  } = useChat();

  const handleRenameFromHeader = (newTitle: string) => {
    if (activeChatId) {
      renameChat(activeChatId, newTitle);
    }
  };

  return (
    <div className="h-screen flex w-full bg-background">
      {/* Sidebar */}
      <ChatSidebar
        groupedChats={groupedChats}
        activeChatId={activeChatId}
        isCollapsed={sidebarCollapsed}
        onSelectChat={setActiveChatId}
        onNewChat={createNewChat}
        onRenameChat={renameChat}
        onDeleteChat={deleteChat}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
      />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <ChatHeader
          title={activeChat?.title || "New conversation"}
          theme={theme}
          onThemeChange={setTheme}
          onRename={handleRenameFromHeader}
        />

        {/* Messages */}
        <ChatMessages chat={activeChat} />

        {/* Input */}
        <ChatInput onSend={sendMessage} isDisabled={isStreaming} />
      </div>
    </div>
  );
};

export default Index;
