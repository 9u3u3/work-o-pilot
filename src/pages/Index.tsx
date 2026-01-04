import { useState } from "react";
import { useChat } from "@/hooks/useChat";
import { useTheme } from "@/hooks/useTheme";
import {
  ChatSidebar,
  ChatHeader,
  ChatMessages,
  ChatInput,
} from "@/components/chat";
import { AssetSidebar } from "@/components/assets/AssetSidebar";
import { ExportDialog } from "@/components/chat/ExportDialog";

const Index = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [assetSidebarOpen, setAssetSidebarOpen] = useState(false);
  const [exportDialogOpen, setExportDialogOpen] = useState(false);
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

  const hasMessages = (activeChat?.messages?.length ?? 0) > 0;

  const handleFollowUpClick = (question: string) => {
    sendMessage(question);
  };

  return (
    <div className="h-screen flex w-full bg-background overflow-hidden">
      {/* Left Sidebar */}
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
      <div className="flex-1 flex flex-col min-w-0 relative">
        {/* Header */}
        <ChatHeader
          title={activeChat?.title || "New conversation"}
          theme={theme}
          onThemeChange={setTheme}
          onRename={handleRenameFromHeader}
          onToggleAssets={() => setAssetSidebarOpen(!assetSidebarOpen)}
          onExport={() => setExportDialogOpen(true)}
          hasMessages={hasMessages}
        />

        {/* Messages */}
        <ChatMessages chat={activeChat} onFollowUpClick={handleFollowUpClick} />

        {/* Input */}
        <ChatInput onSend={sendMessage} isDisabled={isStreaming} />
      </div>

      {/* Right Asset Sidebar */}
      <AssetSidebar
        isOpen={assetSidebarOpen}
        onToggle={() => setAssetSidebarOpen(!assetSidebarOpen)}
      />

      {/* Export Dialog */}
      <ExportDialog
        open={exportDialogOpen}
        onOpenChange={setExportDialogOpen}
        messages={activeChat?.messages || []}
      />
    </div>
  );
};

export default Index;
