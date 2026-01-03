import { useState, useCallback } from "react";
import { Chat, Message, FileAttachment, GroupedChats, DateGroup } from "@/types/chat";
import { mockChats, getRandomMockResponse } from "@/data/mockChats";

function getDateGroup(date: Date): DateGroup {
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const yesterday = new Date(today.getTime() - 24 * 60 * 60 * 1000);
  const lastWeek = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
  const lastMonth = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000);

  const chatDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());

  if (chatDate.getTime() >= today.getTime()) return "Today";
  if (chatDate.getTime() >= yesterday.getTime()) return "Yesterday";
  if (chatDate.getTime() >= lastWeek.getTime()) return "Last 7 days";
  if (chatDate.getTime() >= lastMonth.getTime()) return "Last 30 days";
  return "Older";
}

function groupChatsByDate(chats: Chat[]): GroupedChats[] {
  const groups: Record<DateGroup, Chat[]> = {
    Today: [],
    Yesterday: [],
    "Last 7 days": [],
    "Last 30 days": [],
    Older: [],
  };

  chats.forEach((chat) => {
    const group = getDateGroup(chat.updatedAt);
    groups[group].push(chat);
  });

  const orderedGroups: DateGroup[] = ["Today", "Yesterday", "Last 7 days", "Last 30 days", "Older"];

  return orderedGroups
    .filter((group) => groups[group].length > 0)
    .map((group) => ({
      group,
      chats: groups[group].sort((a, b) => b.updatedAt.getTime() - a.updatedAt.getTime()),
    }));
}

export function useChat() {
  const [chats, setChats] = useState<Chat[]>(mockChats);
  const [activeChatId, setActiveChatId] = useState<string>(mockChats[0]?.id || "");
  const [isStreaming, setIsStreaming] = useState(false);

  const activeChat = chats.find((c) => c.id === activeChatId) || null;
  const groupedChats = groupChatsByDate(chats);

  const createNewChat = useCallback(() => {
    const newChat: Chat = {
      id: crypto.randomUUID(),
      title: "New conversation",
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    setChats((prev) => [newChat, ...prev]);
    setActiveChatId(newChat.id);
    return newChat;
  }, []);

  const deleteChat = useCallback(
    (chatId: string) => {
      setChats((prev) => prev.filter((c) => c.id !== chatId));
      if (activeChatId === chatId) {
        const remaining = chats.filter((c) => c.id !== chatId);
        setActiveChatId(remaining[0]?.id || "");
      }
    },
    [activeChatId, chats]
  );

  const renameChat = useCallback((chatId: string, newTitle: string) => {
    setChats((prev) =>
      prev.map((c) => (c.id === chatId ? { ...c, title: newTitle, updatedAt: new Date() } : c))
    );
  }, []);

  const sendMessage = useCallback(
    async (content: string, attachments?: FileAttachment[]) => {
      let chatId = activeChatId;

      // Create new chat if none exists or current is empty
      if (!chatId) {
        const newChat = createNewChat();
        chatId = newChat.id;
      }

      const userMessage: Message = {
        id: crypto.randomUUID(),
        role: "user",
        content,
        timestamp: new Date(),
        attachments,
      };

      // Add user message
      setChats((prev) =>
        prev.map((c) => {
          if (c.id === chatId) {
            const isFirstMessage = c.messages.length === 0;
            return {
              ...c,
              title: isFirstMessage ? content.slice(0, 40) + (content.length > 40 ? "..." : "") : c.title,
              messages: [...c.messages, userMessage],
              updatedAt: new Date(),
            };
          }
          return c;
        })
      );

      // Simulate AI response
      setIsStreaming(true);

      const aiMessage: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: "",
        timestamp: new Date(),
        isStreaming: true,
      };

      // Add empty AI message
      setChats((prev) =>
        prev.map((c) =>
          c.id === chatId
            ? { ...c, messages: [...c.messages, aiMessage], updatedAt: new Date() }
            : c
        )
      );

      // Simulate streaming response
      const fullResponse = getRandomMockResponse();
      const words = fullResponse.split(" ");
      let currentContent = "";

      for (let i = 0; i < words.length; i++) {
        await new Promise((resolve) => setTimeout(resolve, 30 + Math.random() * 20));
        currentContent += (i > 0 ? " " : "") + words[i];

        setChats((prev) =>
          prev.map((c) => {
            if (c.id === chatId) {
              const messages = [...c.messages];
              const lastMsg = messages[messages.length - 1];
              if (lastMsg && lastMsg.id === aiMessage.id) {
                messages[messages.length - 1] = {
                  ...lastMsg,
                  content: currentContent,
                };
              }
              return { ...c, messages };
            }
            return c;
          })
        );
      }

      // Mark streaming as complete
      setChats((prev) =>
        prev.map((c) => {
          if (c.id === chatId) {
            const messages = [...c.messages];
            const lastMsg = messages[messages.length - 1];
            if (lastMsg && lastMsg.id === aiMessage.id) {
              messages[messages.length - 1] = {
                ...lastMsg,
                isStreaming: false,
              };
            }
            return { ...c, messages, updatedAt: new Date() };
          }
          return c;
        })
      );

      setIsStreaming(false);
    },
    [activeChatId, createNewChat]
  );

  return {
    chats,
    activeChat,
    activeChatId,
    groupedChats,
    isStreaming,
    setActiveChatId,
    createNewChat,
    deleteChat,
    renameChat,
    sendMessage,
  };
}
