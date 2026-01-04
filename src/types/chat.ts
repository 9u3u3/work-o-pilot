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
  visualization?: {
    type: "pie_chart" | "line_chart" | "bar_chart" | "table" | "none";
    chart_data?: {
      type: string;
      labels?: string[];
      values?: number[];
      datasets?: Array<{ label: string; data: Array<{ x: string; y: number }> }>;
      data?: Record<string, unknown>[];
    };
    image_base64?: string;
  };
  sources?: Array<{ name: string; url?: string; type: string }>;
  data?: Record<string, unknown>;
  follow_up_question?: string;
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
