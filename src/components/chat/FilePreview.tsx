import { X } from "lucide-react";
import { FileAttachment } from "@/types/chat";
import { FileIcon, formatFileSize } from "./FileIcon";
import { Button } from "@/components/ui/button";

interface FilePreviewProps {
  attachments: FileAttachment[];
  onRemove: (id: string) => void;
}

export function FilePreview({ attachments, onRemove }: FilePreviewProps) {
  if (attachments.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-2 p-3 border-t border-border">
      {attachments.map((attachment) => (
        <div
          key={attachment.id}
          className="flex items-center gap-2 px-3 py-2 bg-muted rounded-lg group animate-fade-in"
        >
          <FileIcon type={attachment.type} className="h-4 w-4 text-muted-foreground" />
          <div className="flex flex-col">
            <span className="text-sm font-medium text-foreground truncate max-w-[150px]">
              {attachment.name}
            </span>
            <span className="text-xs text-muted-foreground">
              {formatFileSize(attachment.size)}
            </span>
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="h-5 w-5 ml-1 opacity-0 group-hover:opacity-100 transition-opacity"
            onClick={() => onRemove(attachment.id)}
          >
            <X className="h-3 w-3" />
          </Button>
        </div>
      ))}
    </div>
  );
}
