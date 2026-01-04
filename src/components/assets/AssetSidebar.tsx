import { useState } from "react";
import { Plus, TrendingUp, Building2, Wallet, MoreHorizontal, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn, generateUUID } from "@/lib/utils";
import { AssetForm } from "./AssetForm";
import { AssetFormData, Asset } from "@/types/asset";
import { useAssets } from "@/contexts/AssetContext";

interface AssetSidebarProps {
    isOpen: boolean;
    onToggle: () => void;
}

export function AssetSidebar({ isOpen, onToggle }: AssetSidebarProps) {
    const [isFormOpen, setIsFormOpen] = useState(false);
    const { addAsset } = useAssets();

    const handleAddAsset = async (data: AssetFormData, files: File[]) => {
        const newAsset: Asset = {
            id: generateUUID(),
            ...data,
            files,
            quantity: Number(data.quantity),
            avgBuyPrice: Number(data.avgBuyPrice),
            purchaseDate: data.purchaseDate || new Date(),
        };
        await addAsset(newAsset);
    };

    return (
        <>
            <div
                className={cn(
                    "fixed inset-y-0 right-0 z-40 w-64 bg-sidebar border-l border-sidebar-border transform transition-transform duration-300 ease-in-out",
                    isOpen ? "translate-x-0" : "translate-x-full"
                )}
            >
                <div className="h-full flex flex-col">
                    <div className="p-4 border-b border-sidebar-border flex items-center justify-between">
                        <h2 className="font-semibold text-sidebar-foreground">Asset Manager</h2>
                        <Button
                            variant="ghost"
                            size="icon"
                            onClick={onToggle}
                            className="text-sidebar-foreground hover:bg-sidebar-accent"
                        >
                            <ChevronRight className="h-4 w-4" />
                        </Button>
                    </div>

                    <div className="p-4 space-y-4">
                        <div className="space-y-2">
                            <h3 className="text-xs font-medium text-sidebar-foreground/60 uppercase tracking-wider">
                                Add Assets
                            </h3>
                            <Button
                                variant="outline"
                                className="w-full justify-start gap-3 h-auto py-3 border-sidebar-border hover:bg-sidebar-accent hover:text-sidebar-accent-foreground group"
                                onClick={() => setIsFormOpen(true)}
                            >
                                <div className="p-2 rounded-md bg-emerald-500 text-white shadow-sm group-hover:bg-emerald-600 transition-colors">
                                    <TrendingUp className="h-5 w-5" />
                                </div>
                                <div className="flex flex-col items-start">
                                    <span className="font-medium">Stocks/Equities</span>
                                    <span className="text-xs text-muted-foreground group-hover:text-sidebar-accent-foreground/80">
                                        Add stock holdings
                                    </span>
                                </div>
                            </Button>
                        </div>
                    </div>
                </div>
            </div>

            <AssetForm
                isOpen={isFormOpen}
                onClose={() => setIsFormOpen(false)}
                onSubmit={handleAddAsset}
            />
        </>
    );
}
