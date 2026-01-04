export type AssetType = "Stock" | "Crypto" | "Real Estate" | "Other";

export interface Asset {
    id: string;
    symbol: string;
    exchange?: string;
    quantity: number;
    avgBuyPrice: number;
    purchaseDate: Date;
    portfolioName: string;
    currency: string;
    broker?: string;
    investmentType: AssetType;
    additionalInfo?: string;
    files: File[]; // For local uploads
    structuredFileUrls?: string[]; // From backend
    unstructuredFileUrls?: string[]; // From backend
}

export interface AssetFormData {
    symbol: string;
    exchange: string;
    quantity: string;
    avgBuyPrice: string;
    purchaseDate: Date | undefined;
    portfolioName: string;
    currency: string;
    broker: string;
    investmentType: AssetType;
    additionalInfo: string;
}
