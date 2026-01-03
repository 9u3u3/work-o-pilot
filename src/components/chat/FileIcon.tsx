import { FileText, FileSpreadsheet, FileType, File } from "lucide-react";

interface FileIconProps {
  type: string;
  className?: string;
}

export function FileIcon({ type, className = "h-4 w-4" }: FileIconProps) {
  if (type.includes("csv") || type.includes("spreadsheet") || type.includes("excel")) {
    return <FileSpreadsheet className={className} />;
  }
  if (type.includes("pdf")) {
    return <FileType className={className} />;
  }
  if (type.includes("text") || type.includes("markdown")) {
    return <FileText className={className} />;
  }
  return <File className={className} />;
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
}
