import React, { createContext, useContext, useState, ReactNode, useEffect } from "react";
import { Asset } from "@/types/asset";
import { fetchAssets as apiFetchAssets, createAsset, deleteAsset as apiDeleteAsset, USER_ID, AssetResponse } from "@/lib/api";

interface AssetContextType {
    assets: Asset[];
    isLoading: boolean;
    addAsset: (asset: Asset) => Promise<Asset | void>;
    deleteAsset: (id: string, symbol: string) => Promise<void>;
    updateAsset: (asset: Asset) => void;
    refreshAssets: () => Promise<void>;
}

const AssetContext = createContext<AssetContextType | undefined>(undefined);

function mapApiAssetToFrontend(apiAsset: AssetResponse): Asset {
    return {
        id: apiAsset.id,
        symbol: apiAsset.symbol,
        exchange: apiAsset.exchange,
        quantity: Number(apiAsset.quantity),
        avgBuyPrice: Number(apiAsset.avg_buy_price),
        purchaseDate: apiAsset.purchase_date ? new Date(apiAsset.purchase_date) : new Date(),
        portfolioName: apiAsset.portfolio_name || "",
        currency: apiAsset.currency,
        broker: apiAsset.broker,
        investmentType: (apiAsset.investment_type as any) || "Stock",
        additionalInfo: apiAsset.additional_info,
        files: [],
        structuredFileUrls: apiAsset.structured_file_urls || [],
        unstructuredFileUrls: apiAsset.unstructured_file_urls || [],
    };
}

export function AssetProvider({ children }: { children: ReactNode }) {
    const [assets, setAssets] = useState<Asset[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    const refreshAssets = async () => {
        try {
            setIsLoading(true);
            const response = await apiFetchAssets();
            setAssets(response.assets.map(mapApiAssetToFrontend));
        } catch (error) {
            console.error("Failed to fetch assets:", error);
        } finally {
            setIsLoading(false);
        }
    };

    // Load assets on mount
    useEffect(() => {
        refreshAssets();
    }, []);

    const addAsset = async (assetData: Asset) => {
        try {
            const formData = new FormData();
            formData.append("user_id", USER_ID);
            formData.append("symbol", assetData.symbol);
            formData.append("quantity", assetData.quantity.toString());
            formData.append("avg_buy_price", assetData.avgBuyPrice.toString());
            if (assetData.purchaseDate) {
                formData.append("purchase_date", assetData.purchaseDate.toISOString().split('T')[0]);
            }
            if (assetData.portfolioName) formData.append("portfolio_name", assetData.portfolioName);
            formData.append("currency", assetData.currency);
            if (assetData.broker) formData.append("broker", assetData.broker);
            formData.append("investment_type", assetData.investmentType);
            if (assetData.additionalInfo) formData.append("additional_info", assetData.additionalInfo);
            if (assetData.exchange) formData.append("exchange", assetData.exchange);

            // Append files
            assetData.files.forEach((file) => {
                formData.append("files", file);
            });

            const data = await createAsset(formData);
            const newAsset = mapApiAssetToFrontend(data);
            setAssets((prev) => [newAsset, ...prev]);
            return newAsset;
        } catch (error) {
            console.error("Error adding asset:", error);
            throw error;
        }
    };

    const deleteAsset = async (id: string, symbol: string) => {
        try {
            await apiDeleteAsset(symbol);
            setAssets((prev) => prev.filter((a) => a.id !== id));
        } catch (error) {
            console.error("Error deleting asset:", error);
            throw error;
        }
    };

    const updateAsset = (updatedAsset: Asset) => {
        setAssets((prev) =>
            prev.map((a) => (a.id === updatedAsset.id ? updatedAsset : a))
        );
    };

    return (
        <AssetContext.Provider value={{ assets, isLoading, addAsset, deleteAsset, updateAsset, refreshAssets }}>
            {children}
        </AssetContext.Provider>
    );
}

export function useAssets() {
    const context = useContext(AssetContext);
    if (context === undefined) {
        throw new Error("useAssets must be used within an AssetProvider");
    }
    return context;
}
