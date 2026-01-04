import { useState, useRef } from "react";
import { Link } from "react-router-dom";
import { ArrowLeft, Plus, FileText, Trash2, Upload, Pencil } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Badge } from "@/components/ui/badge";
import { Asset, AssetType } from "@/types/asset";
import { AssetForm } from "@/components/assets/AssetForm";
import { format } from "date-fns";
import { useAssets } from "@/contexts/AssetContext";
import { generateUUID } from "@/lib/utils";

export default function AssetsPage() {
    const { assets, addAsset, deleteAsset, updateAsset } = useAssets();
    const [isFormOpen, setIsFormOpen] = useState(false);
    const [selectedType, setSelectedType] = useState<AssetType | "All">("All");
    const [deleteTarget, setDeleteTarget] = useState<{ id: string; symbol: string } | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [uploadAssetId, setUploadAssetId] = useState<string | null>(null);
    const [editingAsset, setEditingAsset] = useState<Asset | undefined>(undefined);

    const filteredAssets =
        selectedType === "All"
            ? assets
            : assets.filter((asset) => asset.investmentType === selectedType);

    const handleDelete = async () => {
        if (deleteTarget) {
            await deleteAsset(deleteTarget.id, deleteTarget.symbol);
            setDeleteTarget(null);
        }
    };

    const handleEdit = (asset: Asset) => {
        setEditingAsset(asset);
        setIsFormOpen(true);
    };

    const handleFormClose = () => {
        setIsFormOpen(false);
        setEditingAsset(undefined);
    };

    const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && uploadAssetId) {
            const newFiles = Array.from(e.target.files);
            const assetToUpdate = assets.find((a) => a.id === uploadAssetId);

            if (assetToUpdate) {
                updateAsset({
                    ...assetToUpdate,
                    files: [...assetToUpdate.files, ...newFiles],
                });
            }

            setUploadAssetId(null);
            if (fileInputRef.current) fileInputRef.current.value = "";
        }
    };

    const triggerFileUpload = (id: string) => {
        setUploadAssetId(id);
        fileInputRef.current?.click();
    };

    return (
        <div className="min-h-screen bg-background p-8">
            <div className="max-w-7xl mx-auto space-y-8">
                {/* Header */}
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <Button variant="ghost" size="icon" asChild>
                            <Link to="/">
                                <ArrowLeft className="h-5 w-5" />
                            </Link>
                        </Button>
                        <div>
                            <h1 className="text-3xl font-bold tracking-tight">Assets</h1>
                            <p className="text-muted-foreground">
                                Manage your investment portfolio
                            </p>
                        </div>
                    </div>
                    <Button onClick={() => setIsFormOpen(true)}>
                        <Plus className="h-4 w-4 mr-2" />
                        Add Asset
                    </Button>
                </div>

                {/* Filters */}
                <div className="flex gap-2 overflow-x-auto pb-2">
                    {(["All", "Stock", "Crypto", "Real Estate", "Other"] as const).map(
                        (type) => (
                            <Button
                                key={type}
                                variant={selectedType === type ? "default" : "outline"}
                                onClick={() => setSelectedType(type)}
                                className="rounded-full"
                            >
                                {type}
                            </Button>
                        )
                    )}
                </div>

                {/* Asset Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {filteredAssets.map((asset) => (
                        <Card key={asset.id} className="group relative overflow-hidden">
                            <CardHeader>
                                <div className="flex justify-between items-start">
                                    <div>
                                        <CardTitle className="text-xl">{asset.symbol}</CardTitle>
                                        <CardDescription>{asset.portfolioName}</CardDescription>
                                    </div>
                                    <Badge variant="secondary">{asset.investmentType}</Badge>
                                </div>
                            </CardHeader>
                            <CardContent className="space-y-2">
                                <div className="flex justify-between text-sm">
                                    <span className="text-muted-foreground">Quantity</span>
                                    <span className="font-medium">{asset.quantity}</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span className="text-muted-foreground">Avg. Price</span>
                                    <span className="font-medium">
                                        {asset.currency} {asset.avgBuyPrice.toLocaleString()}
                                    </span>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span className="text-muted-foreground">Date</span>
                                    <span className="font-medium">
                                        {format(asset.purchaseDate, "PP")}
                                    </span>
                                </div>
                                {asset.exchange && (
                                    <div className="flex justify-between text-sm">
                                        <span className="text-muted-foreground">Exchange</span>
                                        <span className="font-medium">{asset.exchange}</span>
                                    </div>
                                )}
                                {(asset.files.length > 0 || (asset.structuredFileUrls?.length ?? 0) > 0 || (asset.unstructuredFileUrls?.length ?? 0) > 0) && (
                                    <div className="mt-4 pt-4 border-t">
                                        <p className="text-xs text-muted-foreground mb-2">
                                            Attachments
                                        </p>
                                        <div className="flex flex-wrap gap-2">
                                            {/* Local Files */}
                                            {asset.files.map((file, i) => (
                                                <Badge key={`local-${i}`} variant="outline" className="text-xs">
                                                    {file.name}
                                                </Badge>
                                            ))}
                                            {/* Structured Files */}
                                            {asset.structuredFileUrls?.map((url, i) => (
                                                <a key={`struct-${i}`} href={url} target="_blank" rel="noopener noreferrer">
                                                    <Badge variant="outline" className="text-xs hover:bg-accent cursor-pointer">
                                                        CSV/Excel {i + 1}
                                                    </Badge>
                                                </a>
                                            ))}
                                            {/* Unstructured Files */}
                                            {asset.unstructuredFileUrls?.map((url, i) => (
                                                <a key={`unstruct-${i}`} href={url} target="_blank" rel="noopener noreferrer">
                                                    <Badge variant="outline" className="text-xs hover:bg-accent cursor-pointer">
                                                        Doc {i + 1}
                                                    </Badge>
                                                </a>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </CardContent>
                            <CardFooter className="flex justify-between border-t bg-muted/50 p-4">
                                <div className="flex gap-2">
                                    <Button
                                        variant="ghost"
                                        size="icon"
                                        className="h-8 w-8"
                                        onClick={() => handleEdit(asset)}
                                    >
                                        <Pencil className="h-4 w-4" />
                                    </Button>
                                </div>
                                <Button
                                    variant="ghost"
                                    size="icon"
                                    className="h-8 w-8 text-destructive hover:text-destructive hover:bg-destructive/10"
                                    onClick={() => setDeleteTarget({ id: asset.id, symbol: asset.symbol })}
                                >
                                    <Trash2 className="h-4 w-4" />
                                </Button>
                            </CardFooter>
                        </Card>
                    ))}
                </div>

                {filteredAssets.length === 0 && (
                    <div className="text-center py-12">
                        <p className="text-muted-foreground">No assets found.</p>
                    </div>
                )}
            </div>

            <AssetForm
                isOpen={isFormOpen}
                onClose={handleFormClose}
                initialData={editingAsset}
                onSubmit={async (data, files) => {
                    const newAsset: Asset = {
                        id: generateUUID(), // Temp ID, will be replaced by backend
                        ...data,
                        files,
                        quantity: Number(data.quantity),
                        avgBuyPrice: Number(data.avgBuyPrice),
                        purchaseDate: data.purchaseDate || new Date(),
                    };
                    if (editingAsset) {
                        updateAsset({
                            ...editingAsset,
                            ...data,
                            quantity: Number(data.quantity),
                            avgBuyPrice: Number(data.avgBuyPrice),
                            purchaseDate: data.purchaseDate || new Date(),
                            files: [...editingAsset.files, ...files],
                        });
                    } else {
                        await addAsset(newAsset);
                    }
                    handleFormClose();
                }}
            />

            {/* Hidden File Input */}
            <input
                ref={fileInputRef}
                type="file"
                multiple
                className="hidden"
                onChange={handleFileUpload}
            />

            {/* Delete Confirmation Dialog */}
            <AlertDialog open={!!deleteTarget} onOpenChange={() => setDeleteTarget(null)}>
                <AlertDialogContent className="border-destructive/50">
                    <AlertDialogHeader>
                        <AlertDialogTitle className="text-destructive">
                            Delete Asset?
                        </AlertDialogTitle>
                        <AlertDialogDescription>
                            This action cannot be undone. This will permanently delete this
                            asset and all associated files from your portfolio.
                        </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                        <AlertDialogAction
                            onClick={handleDelete}
                            className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                        >
                            Delete Asset
                        </AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>
        </div>
    );
}
