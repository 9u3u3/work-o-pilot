import { useState, useRef, useEffect, KeyboardEvent } from "react";
import { Send, Paperclip, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { FilePreview } from "./FilePreview";
import { useFileUpload } from "@/hooks/useFileUpload";
import { FileAttachment } from "@/types/chat";
import { cn } from "@/lib/utils";

interface ChatInputProps {
  onSend: (content: string, attachments?: FileAttachment[]) => void;
  isDisabled?: boolean;
}

export function ChatInput({ onSend, isDisabled }: ChatInputProps) {
  const [content, setContent] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const {
    attachments,
    inputRef,
    removeAttachment,
    clearAttachments,
    openFilePicker,
    handleFileChange,
    allowedExtensions,
  } = useFileUpload();

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      textarea.style.height = Math.min(textarea.scrollHeight, 200) + "px";
    }
  }, [content]);

  const handleSend = () => {
    const trimmed = content.trim();
    if (!trimmed && attachments.length === 0) return;
    if (isDisabled) return;

    onSend(trimmed, attachments.length > 0 ? attachments : undefined);
    setContent("");
    clearAttachments();

    // Reset height
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const canSend = (content.trim() || attachments.length > 0) && !isDisabled;

  return (
    <div className="border-t border-border bg-background p-4">
      <div className="max-w-3xl mx-auto">
        <div
          className={cn(
            "relative rounded-xl border border-input bg-chat-input-bg shadow-soft transition-shadow",
            "focus-within:ring-2 focus-within:ring-ring focus-within:ring-offset-2 focus-within:ring-offset-background"
          )}
        >
          <Textarea
            ref={textareaRef}
            value={content}
            onChange={(e) => setContent(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask anything about your data..."
            disabled={isDisabled}
            className="min-h-[52px] max-h-[200px] resize-none border-0 bg-transparent px-4 py-3 pr-24 focus-visible:ring-0 focus-visible:ring-offset-0 placeholder:text-muted-foreground"
            rows={1}
          />

          <FilePreview attachments={attachments} onRemove={removeAttachment} />

          {/* Action buttons */}
          <div className="absolute right-2 bottom-2 flex items-center gap-1">
            <input
              ref={inputRef}
              type="file"
              multiple
              accept={allowedExtensions.join(",")}
              onChange={handleFileChange}
              className="hidden"
            />
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="h-8 w-8 text-muted-foreground hover:text-foreground"
              onClick={openFilePicker}
              disabled={isDisabled}
            >
              <Paperclip className="h-4 w-4" />
            </Button>
            <Button
              type="button"
              size="icon"
              className={cn(
                "h-8 w-8 transition-all",
                canSend
                  ? "bg-primary text-primary-foreground hover:bg-primary/90"
                  : "bg-muted text-muted-foreground"
              )}
              onClick={handleSend}
              disabled={!canSend}
            >
              {isDisabled ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>

        <p className="text-xs text-muted-foreground text-center mt-2">
          Press Enter to send, Shift+Enter for new line
        </p>
      </div>
    </div>
  );
}
