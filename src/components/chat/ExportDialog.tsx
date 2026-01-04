import { useState } from "react";
import { Message } from "@/types/chat";
import { generateExportSummary, ExportMessage, USER_ID } from "@/lib/api";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Loader2, FileDown, Check } from "lucide-react";
import { cn } from "@/lib/utils";

interface ExportDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    messages: Message[];
}

export function ExportDialog({ open, onOpenChange, messages }: ExportDialogProps) {
    const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
    const [title, setTitle] = useState("Chat Export");
    const [includeVisualizations, setIncludeVisualizations] = useState(true);
    const [isExporting, setIsExporting] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const toggleMessage = (id: string) => {
        setSelectedIds((prev) => {
            const next = new Set(prev);
            if (next.has(id)) {
                next.delete(id);
            } else {
                next.add(id);
            }
            return next;
        });
    };

    const selectAll = () => {
        setSelectedIds(new Set(messages.map((m) => m.id)));
    };

    const deselectAll = () => {
        setSelectedIds(new Set());
    };

    const handleExport = async () => {
        if (selectedIds.size === 0) {
            setError("Please select at least one message");
            return;
        }

        setIsExporting(true);
        setError(null);

        try {
            const selectedMessages = messages.filter((m) => selectedIds.has(m.id));
            const exportMessages: ExportMessage[] = selectedMessages.map((m) => ({
                role: m.role,
                content: m.content,
                timestamp: m.timestamp.toISOString(),
                has_visualization: !!m.visualization && m.visualization.type !== "none",
                visualization_type: m.visualization?.type || null,
                image_base64: m.visualization?.image_base64 || null,
            }));

            const response = await generateExportSummary({
                user_id: USER_ID,
                messages: exportMessages,
                export_format: "markdown",
                include_visualizations: includeVisualizations,
                title,
            });

            // Generate PDF from the structured content
            await generateAndDownloadPDF(response.structured_content, response.visualizations, response.title);

            onOpenChange(false);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Export failed");
        } finally {
            setIsExporting(false);
        }
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-2xl max-h-[80vh] overflow-hidden flex flex-col">
                <DialogHeader>
                    <DialogTitle>Export Chat</DialogTitle>
                    <DialogDescription>
                        Select messages to export as a PDF report
                    </DialogDescription>
                </DialogHeader>

                <div className="flex-1 overflow-y-auto space-y-4 py-4">
                    {/* Title input */}
                    <div className="space-y-2">
                        <Label htmlFor="export-title">Report Title</Label>
                        <Input
                            id="export-title"
                            value={title}
                            onChange={(e) => setTitle(e.target.value)}
                            placeholder="Enter report title..."
                        />
                    </div>

                    {/* Options */}
                    <div className="flex items-center gap-2">
                        <Checkbox
                            id="include-viz"
                            checked={includeVisualizations}
                            onCheckedChange={(checked) => setIncludeVisualizations(!!checked)}
                        />
                        <Label htmlFor="include-viz" className="text-sm cursor-pointer">
                            Include visualizations/charts
                        </Label>
                    </div>

                    {/* Selection controls */}
                    <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">
                            {selectedIds.size} of {messages.length} messages selected
                        </span>
                        <div className="flex gap-2">
                            <Button variant="outline" size="sm" onClick={selectAll}>
                                Select All
                            </Button>
                            <Button variant="outline" size="sm" onClick={deselectAll}>
                                Deselect All
                            </Button>
                        </div>
                    </div>

                    {/* Message list */}
                    <div className="border rounded-lg divide-y max-h-[300px] overflow-y-auto">
                        {messages.map((message) => (
                            <div
                                key={message.id}
                                className={cn(
                                    "flex items-start gap-3 p-3 cursor-pointer hover:bg-accent/50 transition-colors",
                                    selectedIds.has(message.id) && "bg-accent"
                                )}
                                onClick={() => toggleMessage(message.id)}
                            >
                                <Checkbox
                                    checked={selectedIds.has(message.id)}
                                    onCheckedChange={() => toggleMessage(message.id)}
                                    className="mt-0.5"
                                />
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2 mb-1">
                                        <span className={cn(
                                            "text-xs font-medium px-2 py-0.5 rounded",
                                            message.role === "user"
                                                ? "bg-primary/10 text-primary"
                                                : "bg-secondary text-secondary-foreground"
                                        )}>
                                            {message.role === "user" ? "You" : "AI"}
                                        </span>
                                        {message.visualization && message.visualization.type !== "none" && (
                                            <span className="text-xs text-muted-foreground">
                                                📊 {message.visualization.type.replace("_", " ")}
                                            </span>
                                        )}
                                    </div>
                                    <p className="text-sm text-muted-foreground line-clamp-2">
                                        {message.content}
                                    </p>
                                </div>
                            </div>
                        ))}
                    </div>

                    {error && (
                        <p className="text-sm text-destructive">{error}</p>
                    )}
                </div>

                <DialogFooter>
                    <Button variant="outline" onClick={() => onOpenChange(false)}>
                        Cancel
                    </Button>
                    <Button onClick={handleExport} disabled={isExporting || selectedIds.size === 0}>
                        {isExporting ? (
                            <>
                                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                Generating...
                            </>
                        ) : (
                            <>
                                <FileDown className="h-4 w-4 mr-2" />
                                Export PDF
                            </>
                        )}
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}

// PDF Generation using browser print API
async function generateAndDownloadPDF(
    markdownContent: string,
    visualizations: Array<{ caption: string; image_base64: string }>,
    title: string
) {
    // Create a new window for printing
    const printWindow = window.open("", "_blank");
    if (!printWindow) {
        throw new Error("Could not open print window. Please allow popups.");
    }

    // Convert markdown to basic HTML (simple conversion)
    let htmlContent = markdownContent
        .replace(/^### (.*$)/gm, "<h3>$1</h3>")
        .replace(/^## (.*$)/gm, "<h2>$1</h2>")
        .replace(/^# (.*$)/gm, "<h1>$1</h1>")
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(/\*(.*?)\*/g, "<em>$1</em>")
        .replace(/^- (.*$)/gm, "<li>$1</li>")
        .replace(/(<li>.*<\/li>)/s, "<ul>$1</ul>")
        .replace(/\n\n/g, "</p><p>")
        .replace(/^(?!<[hulo])/gm, "<p>")
        .replace(/(?<![>])$/gm, "</p>");

    // Add visualizations
    const vizHtml = visualizations.map((viz, i) => `
        <figure style="margin: 20px 0; text-align: center;">
            <img src="data:image/png;base64,${viz.image_base64}" 
                 alt="${viz.caption}" 
                 style="max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 8px;" />
            <figcaption style="margin-top: 8px; font-size: 14px; color: #666;">${viz.caption}</figcaption>
        </figure>
    `).join("");

    const fullHtml = `
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>${title}</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 40px 20px;
                    color: #333;
                }
                h1 { font-size: 28px; margin-bottom: 8px; }
                h2 { font-size: 22px; margin-top: 32px; color: #444; }
                h3 { font-size: 18px; margin-top: 24px; color: #555; }
                p { margin: 12px 0; }
                ul { padding-left: 24px; }
                li { margin: 8px 0; }
                .header {
                    border-bottom: 2px solid #333;
                    padding-bottom: 16px;
                    margin-bottom: 32px;
                }
                .generated-date {
                    font-size: 12px;
                    color: #888;
                }
                @media print {
                    body { padding: 0; }
                    figure { page-break-inside: avoid; }
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>${title}</h1>
                <p class="generated-date">Generated on ${new Date().toLocaleDateString()}</p>
            </div>
            ${htmlContent}
            ${vizHtml ? `<h2>Visualizations</h2>${vizHtml}` : ""}
        </body>
        </html>
    `;

    printWindow.document.write(fullHtml);
    printWindow.document.close();

    // Wait for images to load then trigger print
    printWindow.onload = () => {
        setTimeout(() => {
            printWindow.print();
        }, 500);
    };
}
