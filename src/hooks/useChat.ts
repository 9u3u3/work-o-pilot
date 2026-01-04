import { useState, useCallback, useEffect } from "react";
import { Chat, Message, FileAttachment, GroupedChats, DateGroup } from "@/types/chat";
import { sendChatMessage, fetchConversations, fetchConversationHistory, USER_ID } from "@/lib/api";
import { generateUUID } from "@/lib/utils";

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
  const [chats, setChats] = useState<Chat[]>([]);
  const [activeChatId, setActiveChatId] = useState<string>("");
  const [isStreaming, setIsStreaming] = useState(false);

  const activeChat = chats.find((c) => c.id === activeChatId) || null;
  const groupedChats = groupChatsByDate(chats);

  // Load conversations on mount (gracefully handle backend unavailable)
  useEffect(() => {
    async function loadConversations() {
      try {
        const conversations = await fetchConversations();
        if (conversations && conversations.length > 0) {
          const loadedChats: Chat[] = conversations.map((conv) => ({
            id: conv.id,
            title: conv.title || "Conversation",
            messages: [],
            createdAt: new Date(conv.created_at),
            updatedAt: new Date(conv.updated_at),
          }));
          setChats(loadedChats);
          setActiveChatId(loadedChats[0].id);
        }
        // If no conversations, leave chats empty - user can create new
      } catch (error) {
        console.log("Backend not available, starting fresh:", error);
        // Backend not available - that's fine, user can still use local chats
      }
    }
    loadConversations();
  }, []);

  // Load messages when active chat changes
  useEffect(() => {
    async function loadMessages() {
      if (!activeChatId) return;
      const chat = chats.find((c) => c.id === activeChatId);
      if (chat && chat.messages.length > 0) return; // Already loaded

      try {
        const history = await fetchConversationHistory(activeChatId);
        const messages: Message[] = history.map((msg) => ({
          id: msg.id,
          role: msg.role,
          content: msg.content,
          timestamp: new Date(msg.created_at),
          visualization: msg.visualization,
          sources: msg.sources,
        }));
        setChats((prev) =>
          prev.map((c) => (c.id === activeChatId ? { ...c, messages } : c))
        );
      } catch (error) {
        console.error("Failed to load messages:", error);
      }
    }
    loadMessages();
  }, [activeChatId]);

  const createNewChat = useCallback(() => {
    const newChat: Chat = {
      id: generateUUID(),
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
      let conversationId: string | undefined = activeChatId;
      let isNewChat = false;

      // Create new chat if none exists
      if (!chatId) {
        chatId = generateUUID();
        conversationId = undefined;
        isNewChat = true;
      }

      const userMessage: Message = {
        id: generateUUID(),
        role: "user",
        content,
        timestamp: new Date(),
        attachments,
      };

      // Add user message (and create chat if needed)
      if (isNewChat) {
        const newChat: Chat = {
          id: chatId,
          title: content.slice(0, 40) + (content.length > 40 ? "..." : ""),
          messages: [userMessage],
          createdAt: new Date(),
          updatedAt: new Date(),
        };
        setChats((prev) => [newChat, ...prev]);
        setActiveChatId(chatId);
      } else {
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
      }

      // Call API
      setIsStreaming(true);
      try {
        const response = await sendChatMessage({
          user_id: USER_ID,
          conversation_id: conversationId,
          user_query: content,
        });

        const assistantMessage: Message = {
          id: response.message_id,
          role: "assistant",
          content: response.response.text,
          timestamp: new Date(),
          visualization: response.response.visualization,
          sources: response.sources,
          data: response.response.data,
          follow_up_question: response.response.follow_up_question,
        };

        // Update chat with assistant message
        const finalChatId = chatId;
        setChats((prev) =>
          prev.map((c) => {
            if (c.id === finalChatId) {
              return {
                ...c,
                id: response.conversation_id || c.id, // Update to server ID if provided
                messages: [...c.messages, assistantMessage],
                updatedAt: new Date(),
              };
            }
            return c;
          })
        );
        if (response.conversation_id) {
          setActiveChatId(response.conversation_id);
        }
      } catch (error) {
        console.error("Chat error:", error);
        // Add error message
        const errorMessage: Message = {
          id: generateUUID(),
          role: "assistant",
          content: "Sorry, I encountered an error connecting to the server. Please check if the backend is running.",
          timestamp: new Date(),
        };
        setChats((prev) =>
          prev.map((c) =>
            c.id === chatId ? { ...c, messages: [...c.messages, errorMessage] } : c
          )
        );
      } finally {
        setIsStreaming(false);
      }
    },
    [activeChatId]
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
