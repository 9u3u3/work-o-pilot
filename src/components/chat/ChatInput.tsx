import { useState, useRef, useEffect, KeyboardEvent } from "react";
import { Send, Loader2, Paperclip, X, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { FileAttachment } from "@/types/chat";
import { cn, generateUUID } from "@/lib/utils";
import { ingestDocuments } from "@/lib/api";
import { Badge } from "@/components/ui/badge";

interface ChatInputProps {
  onSend: (content: string, attachments?: FileAttachment[]) => void;
  isDisabled?: boolean;
}

export function ChatInput({ onSend, isDisabled }: ChatInputProps) {
  const [content, setContent] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      textarea.style.height = Math.min(textarea.scrollHeight, 200) + "px";
    }
  }, [content]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles((prev) => [...prev, ...Array.from(e.target.files!)]);
    }
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleSend = async () => {
    const trimmed = content.trim();
    if (!trimmed && files.length === 0) return;
    if (isDisabled || isUploading) return;

    // If there are files, ingest them first
    if (files.length > 0) {
      setIsUploading(true);
      try {
        await ingestDocuments(files);
      } catch (error) {
        console.error("Failed to ingest documents:", error);
      } finally {
        setIsUploading(false);
      }
    }

    // Convert files to attachments for display
    const attachments: FileAttachment[] = files.map((file) => ({
      id: generateUUID(),
      name: file.name,
      type: file.type,
      size: file.size,
      file,
    }));

    onSend(trimmed || "I've uploaded some documents for analysis.", attachments.length > 0 ? attachments : undefined);
    setContent("");
    setFiles([]);

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

  const canSend = (content.trim().length > 0 || files.length > 0) && !isDisabled && !isUploading;

  return (
    <div className="border-t border-border bg-background p-4">
      <div className="max-w-3xl mx-auto">
        {/* File Preview */}
        {files.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-2">
            {files.map((file, i) => (
              <Badge key={i} variant="secondary" className="flex items-center gap-1 py-1">
                <FileText className="h-3 w-3" />
                <span className="max-w-[100px] truncate">{file.name}</span>
                <button onClick={() => removeFile(i)} className="ml-1 hover:text-destructive">
                  <X className="h-3 w-3" />
                </button>
              </Badge>
            ))}
          </div>
        )}

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
            disabled={isDisabled || isUploading}
            className="min-h-[52px] max-h-[200px] resize-none border-0 bg-transparent px-4 py-3 pr-24 focus-visible:ring-0 focus-visible:ring-offset-0 placeholder:text-muted-foreground"
            rows={1}
          />

          {/* Action buttons */}
          <div className="absolute right-2 bottom-2 flex items-center gap-1">
            {/* File Upload */}
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept=".txt,.md,.csv,.pdf"
              className="hidden"
              onChange={handleFileSelect}
            />
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              onClick={() => fileInputRef.current?.click()}
              disabled={isDisabled || isUploading}
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
              {isDisabled || isUploading ? (
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
