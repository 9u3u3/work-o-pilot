// API Client for Stock Analytics AI Copilot
const API_BASE = "/api";
export const USER_ID = "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11";

// ============ CHAT API ============
export interface ChatRequest {
    user_id: string;
    conversation_id?: string;
    user_query: string;
}

export interface ChartData {
    type: "pie_chart" | "line_chart" | "bar_chart" | "table";
    labels?: string[];
    values?: number[];
    datasets?: Array<{
        label: string;
        data: Array<{ x: string; y: number }>;
    }>;
    data?: Record<string, unknown>[];
}

export interface Source {
    name: string;
    url?: string;
    type: string;
}

export interface ChatResponse {
    conversation_id: string;
    message_id: string;
    response: {
        text: string;
        data?: Record<string, unknown>;
        visualization?: {
            type: "pie_chart" | "line_chart" | "bar_chart" | "table" | "none";
            chart_data?: ChartData;
            image_base64?: string;
        };
        follow_up_question?: string;
    };
    sources?: Source[];
}

export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
    const res = await fetch(`${API_BASE}/chat/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(request),
    });
    if (!res.ok) throw new Error(`Chat failed: ${res.statusText}`);
    return res.json();
}

// ============ ASSETS API ============
export interface AssetResponse {
    id: string;
    user_id: string;
    symbol: string;
    quantity: number;
    avg_buy_price: number;
    purchase_date?: string;
    portfolio_name?: string;
    currency: string;
    broker?: string;
    exchange?: string;
    investment_type?: string;
    additional_info?: string;
    structured_file_urls?: string[];
    unstructured_file_urls?: string[];
}

export interface AssetsListResponse {
    user_id: string;
    count: number;
    assets: AssetResponse[];
}

export async function fetchAssets(): Promise<AssetsListResponse> {
    const res = await fetch(`${API_BASE}/assets/${USER_ID}`);
    if (!res.ok) throw new Error(`Fetch assets failed: ${res.statusText}`);
    return res.json();
}

export async function deleteAsset(symbol: string): Promise<void> {
    const res = await fetch(`${API_BASE}/assets/${USER_ID}/${symbol}`, {
        method: "DELETE",
    });
    if (!res.ok) throw new Error(`Delete asset failed: ${res.statusText}`);
}

export async function createAsset(formData: FormData): Promise<AssetResponse> {
    const res = await fetch(`${API_BASE}/assets/`, {
        method: "POST",
        body: formData,
    });
    if (!res.ok) throw new Error(`Create asset failed: ${res.statusText}`);
    return res.json();
}

// ============ DOCUMENTS API ============
export interface IngestResponse {
    success: boolean;
    ingested: Array<{ file: string; chunks: number; status: string }>;
    errors: string[];
    total_files: number;
    successful: number;
    failed: number;
}

export async function ingestDocuments(files: File[]): Promise<IngestResponse> {
    const formData = new FormData();
    formData.append("user_id", USER_ID);
    files.forEach((file) => formData.append("files[]", file));

    const res = await fetch(`${API_BASE}/documents/ingest`, {
        method: "POST",
        body: formData,
    });
    if (!res.ok) throw new Error(`Ingest failed: ${res.statusText}`);
    return res.json();
}

// ============ CHAT HISTORY API ============
export interface ConversationSummary {
    id: string;
    title?: string;
    created_at: string;
    updated_at: string;
}

export interface HistoryMessage {
    id: string;
    role: "user" | "assistant";
    content: string;
    created_at: string;
    visualization?: ChatResponse["response"]["visualization"];
    sources?: Source[];
}

export async function fetchConversations(): Promise<ConversationSummary[]> {
    const res = await fetch(`${API_BASE}/chat/conversations/${USER_ID}`);
    if (!res.ok) throw new Error(`Fetch conversations failed: ${res.statusText}`);
    return res.json();
}

export async function fetchConversationHistory(conversationId: string): Promise<HistoryMessage[]> {
    const res = await fetch(`${API_BASE}/chat/history/${conversationId}`);
    if (!res.ok) throw new Error(`Fetch history failed: ${res.statusText}`);
    return res.json();
}

// ============ EXPORT API ============
export interface ExportMessage {
    role: "user" | "assistant";
    content: string;
    timestamp: string;
    has_visualization: boolean;
    visualization_type: string | null;
    image_base64: string | null;
}

export interface ExportRequest {
    user_id: string;
    messages: ExportMessage[];
    export_format: "markdown" | "pdf";
    include_visualizations: boolean;
    title?: string;
}

export interface ExportSection {
    title: string;
    content: string;
    level: number;
}

export interface ExportVisualization {
    caption: string;
    image_base64: string;
}

export interface ExportResponse {
    title: string;
    summary: string;
    structured_content: string;
    sections: ExportSection[];
    visualizations: ExportVisualization[];
    generated_at: string;
}

export async function generateExportSummary(request: ExportRequest): Promise<ExportResponse> {
    const res = await fetch(`${API_BASE}/export/generate-summary`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(request),
    });
    if (!res.ok) throw new Error(`Export failed: ${res.statusText}`);
    return res.json();
}
