import { useMemo } from "react";
import { cn } from "@/lib/utils";

interface MarkdownRendererProps {
  content: string;
  isStreaming?: boolean;
}

export function MarkdownRenderer({ content, isStreaming }: MarkdownRendererProps) {
  const rendered = useMemo(() => parseMarkdown(content), [content]);

  return (
    <div
      className={cn(
        "prose prose-sm max-w-none dark:prose-invert",
        "prose-headings:font-semibold prose-headings:text-foreground",
        "prose-p:text-foreground prose-p:leading-relaxed",
        "prose-strong:text-foreground prose-strong:font-semibold",
        "prose-code:bg-code-bg prose-code:text-code-fg prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:text-sm prose-code:font-mono",
        "prose-pre:bg-code-bg prose-pre:border prose-pre:border-border prose-pre:rounded-lg",
        "prose-table:border-collapse prose-th:border prose-th:border-border prose-th:px-3 prose-th:py-2 prose-th:bg-muted prose-th:text-left prose-th:font-medium",
        "prose-td:border prose-td:border-border prose-td:px-3 prose-td:py-2",
        "prose-ul:list-disc prose-ol:list-decimal prose-li:text-foreground",
        "prose-a:text-primary prose-a:no-underline hover:prose-a:underline",
        isStreaming && "typing-cursor"
      )}
      dangerouslySetInnerHTML={{ __html: rendered }}
    />
  );
}

function parseMarkdown(text: string): string {
  let html = text;

  // Code blocks (```code```)
  html = html.replace(/```(\w+)?\n([\s\S]*?)```/g, (_, lang, code) => {
    return `<pre class="relative group"><code class="language-${lang || "text"}">${escapeHtml(code.trim())}</code></pre>`;
  });

  // Inline code (`code`)
  html = html.replace(/`([^`]+)`/g, "<code>$1</code>");

  // Headers
  html = html.replace(/^### (.+)$/gm, "<h3>$1</h3>");
  html = html.replace(/^## (.+)$/gm, "<h2>$1</h2>");
  html = html.replace(/^# (.+)$/gm, "<h1>$1</h1>");

  // Bold (**text**)
  html = html.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");

  // Italic (*text*)
  html = html.replace(/\*([^*]+)\*/g, "<em>$1</em>");

  // Tables
  html = parseTable(html);

  // Unordered lists
  html = html.replace(/^- (.+)$/gm, "<li>$1</li>");
  html = html.replace(/(<li>.*<\/li>\n?)+/g, "<ul>$&</ul>");

  // Ordered lists
  html = html.replace(/^\d+\. (.+)$/gm, "<li>$1</li>");

  // Line breaks
  html = html.replace(/\n\n/g, "</p><p>");
  html = html.replace(/\n/g, "<br>");

  // Wrap in paragraph if not already wrapped
  if (!html.startsWith("<")) {
    html = `<p>${html}</p>`;
  }

  return html;
}

function parseTable(html: string): string {
  const lines = html.split("\n");
  let inTable = false;
  let tableHtml = "";
  const result: string[] = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    if (line.startsWith("|") && line.endsWith("|")) {
      if (!inTable) {
        inTable = true;
        tableHtml = "<table><thead><tr>";
      }

      // Check if this is the separator row
      if (line.match(/^\|[\s\-:|]+\|$/)) {
        tableHtml += "</tr></thead><tbody>";
        continue;
      }

      const cells = line
        .slice(1, -1)
        .split("|")
        .map((c) => c.trim());

      if (tableHtml.includes("</thead>")) {
        tableHtml += "<tr>";
        cells.forEach((cell) => {
          tableHtml += `<td>${cell}</td>`;
        });
        tableHtml += "</tr>";
      } else {
        cells.forEach((cell) => {
          tableHtml += `<th>${cell}</th>`;
        });
      }
    } else {
      if (inTable) {
        tableHtml += "</tbody></table>";
        result.push(tableHtml);
        tableHtml = "";
        inTable = false;
      }
      result.push(line);
    }
  }

  if (inTable) {
    tableHtml += "</tbody></table>";
    result.push(tableHtml);
  }

  return result.join("\n");
}

function escapeHtml(text: string): string {
  const map: Record<string, string> = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;",
  };
  return text.replace(/[&<>"']/g, (m) => map[m]);
}
