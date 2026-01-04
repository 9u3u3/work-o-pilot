import { useRef, useEffect } from "react";
import { Chat } from "@/types/chat";
import { ChatMessage } from "./ChatMessage";
import { BarChart3, Sparkles, FileSearch, TrendingUp } from "lucide-react";

interface ChatMessagesProps {
  chat: Chat | null;
  onFollowUpClick?: (question: string) => void;
}

const suggestions = [
  {
    icon: BarChart3,
    title: "Analyze revenue data",
    description: "Upload a CSV and get instant insights",
  },
  {
    icon: TrendingUp,
    title: "Track performance metrics",
    description: "Monitor KPIs and identify trends",
  },
  {
    icon: FileSearch,
    title: "Query your documents",
    description: "Ask questions about uploaded files",
  },
  {
    icon: Sparkles,
    title: "Generate reports",
    description: "Create summaries and visualizations",
  },
];

export function ChatMessages({ chat, onFollowUpClick }: ChatMessagesProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chat?.messages]);

  if (!chat || chat.messages.length === 0) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-8">
        <div className="max-w-2xl w-full text-center">
          <h1 className="text-3xl font-semibold text-foreground mb-2">
            Work-o-pilot
          </h1>
          <p className="text-muted-foreground mb-8">
            Your AI assistant for data analysis and insights
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {suggestions.map((suggestion) => (
              <button
                key={suggestion.title}
                className="flex items-start gap-3 p-4 rounded-xl border border-border bg-card hover:bg-chat-hover transition-colors text-left group"
              >
                <div className="p-2 rounded-lg bg-primary/10 text-primary group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                  <suggestion.icon className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="font-medium text-foreground">
                    {suggestion.title}
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    {suggestion.description}
                  </p>
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      ref={scrollRef}
      className="flex-1 overflow-y-auto scrollbar-thin px-4 md:px-8"
    >
      <div className="max-w-3xl mx-auto py-6">
        {chat.messages.map((message) => (
          <ChatMessage
            key={message.id}
            message={message}
            onFollowUpClick={onFollowUpClick}
          />
        ))}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
}
