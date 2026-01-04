import { Message } from "@/types/chat";
import { MarkdownRenderer } from "./MarkdownRenderer";
import { FileIcon, formatFileSize } from "./FileIcon";
import { ChatVisualization } from "./ChatVisualization";
import { cn } from "@/lib/utils";
import { User, Bot, ExternalLink, Sparkles } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

interface ChatMessageProps {
  message: Message;
  onFollowUpClick?: (question: string) => void;
}

export function ChatMessage({ message, onFollowUpClick }: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={cn(
        "flex gap-3 py-4 animate-fade-in",
        isUser ? "flex-row-reverse" : "flex-row"
      )}
    >
      {/* Avatar */}
      <div
        className={cn(
          "flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center",
          isUser ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"
        )}
      >
        {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
      </div>

      {/* Message content */}
      <div
        className={cn(
          "flex flex-col gap-2 max-w-[80%]",
          isUser ? "items-end" : "items-start"
        )}
      >
        {/* Attachments */}
        {message.attachments && message.attachments.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {message.attachments.map((attachment) => (
              <div
                key={attachment.id}
                className="flex items-center gap-2 px-3 py-2 bg-muted rounded-lg"
              >
                <FileIcon type={attachment.type} className="h-4 w-4 text-muted-foreground" />
                <div className="flex flex-col">
                  <span className="text-sm font-medium truncate max-w-[150px]">
                    {attachment.name}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    {formatFileSize(attachment.size)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Text content */}
        {message.content && (
          <div
            className={cn(
              "rounded-xl px-4 py-3",
              isUser
                ? "bg-chat-user-bg text-chat-user-fg"
                : "bg-chat-ai-bg text-chat-ai-fg"
            )}
          >
            {isUser ? (
              <p className="text-sm whitespace-pre-wrap">{message.content}</p>
            ) : (
              <MarkdownRenderer
                content={message.content}
                isStreaming={message.isStreaming}
              />
            )}
          </div>
        )}

        {/* Visualization */}
        {!isUser && message.visualization && message.visualization.type !== "none" && (
          <div className="w-full bg-card border border-border rounded-xl p-4">
            <ChatVisualization visualization={message.visualization} />
          </div>
        )}

        {/* Sources */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="flex flex-col gap-2 mt-2 w-full">
            <span className="text-xs text-muted-foreground font-medium">Sources:</span>
            <div className="flex flex-wrap gap-2">
              {message.sources.map((source, i) => (
                source.url ? (
                  <a
                    key={i}
                    href={source.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-primary/10 hover:bg-primary/20 border border-primary/20 rounded-full text-xs font-medium text-primary transition-colors"
                  >
                    <ExternalLink className="h-3 w-3" />
                    {source.name}
                  </a>
                ) : (
                  <Badge key={i} variant="secondary" className="text-xs px-3 py-1.5">
                    {source.name}
                  </Badge>
                )
              ))}
            </div>
          </div>
        )}

        {/* Follow-up Question */}
        {!isUser && message.follow_up_question && (
          <div className="mt-2">
            <Button
              variant="outline"
              size="sm"
              className="h-auto py-2 px-3 text-left gap-2 bg-gradient-to-r from-primary/5 to-primary/10 hover:from-primary/10 hover:to-primary/20 border-primary/20"
              onClick={() => onFollowUpClick?.(message.follow_up_question!)}
            >
              <Sparkles className="h-3.5 w-3.5 text-primary flex-shrink-0" />
              <span className="text-sm">{message.follow_up_question}</span>
            </Button>
          </div>
        )}

        {/* Timestamp */}
        <span className="text-xs text-muted-foreground">
          {formatTime(message.timestamp)}
        </span>
      </div>
    </div>
  );
}

function formatTime(date: Date): string {
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}
