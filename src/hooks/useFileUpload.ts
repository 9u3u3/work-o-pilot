import { useState, useRef, useCallback } from "react";
import { FileAttachment } from "@/types/chat";

const ALLOWED_TYPES = [
  "text/csv",
  "application/vnd.ms-excel",
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  "application/pdf",
  "text/plain",
  "text/markdown",
];

const ALLOWED_EXTENSIONS = [".csv", ".xls", ".xlsx", ".pdf", ".txt", ".md"];

export function useFileUpload() {
  const [attachments, setAttachments] = useState<FileAttachment[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);

  const isValidFile = useCallback((file: File): boolean => {
    const hasValidType = ALLOWED_TYPES.includes(file.type);
    const hasValidExtension = ALLOWED_EXTENSIONS.some((ext) =>
      file.name.toLowerCase().endsWith(ext)
    );
    return hasValidType || hasValidExtension;
  }, []);

  const addFiles = useCallback(
    (files: FileList | File[]) => {
      const newAttachments: FileAttachment[] = [];

      Array.from(files).forEach((file) => {
        if (isValidFile(file)) {
          newAttachments.push({
            id: crypto.randomUUID(),
            name: file.name,
            type: file.type || getTypeFromExtension(file.name),
            size: file.size,
            file,
          });
        }
      });

      if (newAttachments.length > 0) {
        setAttachments((prev) => [...prev, ...newAttachments]);
      }
    },
    [isValidFile]
  );

  const removeAttachment = useCallback((id: string) => {
    setAttachments((prev) => prev.filter((a) => a.id !== id));
  }, []);

  const clearAttachments = useCallback(() => {
    setAttachments([]);
  }, []);

  const openFilePicker = useCallback(() => {
    inputRef.current?.click();
  }, []);

  const handleFileChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.files) {
        addFiles(e.target.files);
        e.target.value = "";
      }
    },
    [addFiles]
  );

  return {
    attachments,
    inputRef,
    addFiles,
    removeAttachment,
    clearAttachments,
    openFilePicker,
    handleFileChange,
    allowedExtensions: ALLOWED_EXTENSIONS,
  };
}

function getTypeFromExtension(filename: string): string {
  const ext = filename.toLowerCase().split(".").pop();
  switch (ext) {
    case "csv":
      return "text/csv";
    case "xls":
      return "application/vnd.ms-excel";
    case "xlsx":
      return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet";
    case "pdf":
      return "application/pdf";
    case "txt":
      return "text/plain";
    case "md":
      return "text/markdown";
    default:
      return "application/octet-stream";
  }
}
