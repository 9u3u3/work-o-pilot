export interface FileAttachment {
  id: string;
  name: string;
  type: string;
  size: number;
  file: File;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  attachments?: FileAttachment[];
  isStreaming?: boolean;
}

export interface Chat {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
}

export type DateGroup = "Today" | "Yesterday" | "Last 7 days" | "Last 30 days" | "Older";

export interface GroupedChats {
  group: DateGroup;
  chats: Chat[];
}
