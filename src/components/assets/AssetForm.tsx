import { useState, useRef, useEffect } from "react";
import { X, Upload, FileText, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { Calendar } from "@/components/ui/calendar";
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from "@/components/ui/popover";
import { format } from "date-fns";
import { Calendar as CalendarIcon } from "lucide-react";
import { cn } from "@/lib/utils";
import { AssetFormData, AssetType, Asset } from "@/types/asset";

interface AssetFormProps {
    isOpen: boolean;
    onClose: () => void;
    onSubmit: (data: AssetFormData, files: File[]) => void;
    initialData?: Asset;
}

export function AssetForm({
    isOpen,
    onClose,
    onSubmit,
    initialData,
}: AssetFormProps) {
    const [formData, setFormData] = useState<AssetFormData>({
        symbol: "",
        exchange: "",
        quantity: "",
        avgBuyPrice: "",
        purchaseDate: undefined,
        portfolioName: "",
        currency: "USD",
        broker: "",
        investmentType: "Stock",
        additionalInfo: "",
    });
    const [files, setFiles] = useState<File[]>([]);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [isSubmitting, setIsSubmitting] = useState(false);

    useEffect(() => {
        if (isOpen && initialData) {
            setFormData({
                symbol: initialData.symbol,
                exchange: initialData.exchange || "",
                quantity: initialData.quantity.toString(),
                avgBuyPrice: initialData.avgBuyPrice.toString(),
                purchaseDate: initialData.purchaseDate,
                portfolioName: initialData.portfolioName,
                currency: initialData.currency,
                broker: initialData.broker || "",
                investmentType: initialData.investmentType,
                additionalInfo: initialData.additionalInfo || "",
            });
            // Note: We don't populate files here as they are handled separately or require re-upload
        } else if (isOpen && !initialData) {
            // Reset form when opening in add mode
            setFormData({
                symbol: "",
                exchange: "",
                quantity: "",
                avgBuyPrice: "",
                purchaseDate: undefined,
                portfolioName: "",
                currency: "USD",
                broker: "",
                investmentType: "Stock",
                additionalInfo: "",
            });
            setFiles([]);
        }
    }, [isOpen, initialData]);

    if (!isOpen) return null;

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) {
            setFiles((prev) => [...prev, ...Array.from(e.target.files || [])]);
        }
    };

    const removeFile = (index: number) => {
        setFiles((prev) => prev.filter((_, i) => i !== index));
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        setIsSubmitting(true);
        // Simulate API call
        setTimeout(() => {
            onSubmit(formData, files);
            setIsSubmitting(false);
            onClose();
        }, 1000);
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
            <div className="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto bg-background/80 backdrop-blur-md border border-border rounded-xl shadow-2xl p-6">
                <Button
                    variant="ghost"
                    size="icon"
                    className="absolute right-4 top-4"
                    onClick={onClose}
                >
                    <X className="h-4 w-4" />
                </Button>

                <h2 className="text-2xl font-bold mb-6">
                    {initialData ? "Edit Asset" : "Add New Asset"}
                </h2>

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <Label>Stock Symbol</Label>
                            <Input
                                required
                                placeholder="e.g., AAPL"
                                value={formData.symbol}
                                onChange={(e) =>
                                    setFormData({ ...formData, symbol: e.target.value })
                                }
                            />
                        </div>
                        <div className="space-y-2">
                            <Label>Exchange</Label>
                            <Input
                                placeholder="e.g., NASDAQ"
                                value={formData.exchange}
                                onChange={(e) =>
                                    setFormData({ ...formData, exchange: e.target.value })
                                }
                            />
                        </div>
                        <div className="space-y-2">
                            <Label>Quantity</Label>
                            <Input
                                required
                                type="number"
                                step="any"
                                placeholder="0.00"
                                value={formData.quantity}
                                onChange={(e) =>
                                    setFormData({ ...formData, quantity: e.target.value })
                                }
                            />
                        </div>
                        <div className="space-y-2">
                            <Label>Avg Buy Price</Label>
                            <Input
                                required
                                type="number"
                                step="any"
                                placeholder="0.00"
                                value={formData.avgBuyPrice}
                                onChange={(e) =>
                                    setFormData({ ...formData, avgBuyPrice: e.target.value })
                                }
                            />
                        </div>
                        <div className="space-y-2">
                            <Label>Purchase Date</Label>
                            <Popover>
                                <PopoverTrigger asChild>
                                    <Button
                                        variant={"outline"}
                                        className={cn(
                                            "w-full justify-start text-left font-normal",
                                            !formData.purchaseDate && "text-muted-foreground"
                                        )}
                                    >
                                        <CalendarIcon className="mr-2 h-4 w-4" />
                                        {formData.purchaseDate ? (
                                            format(formData.purchaseDate, "PPP")
                                        ) : (
                                            <span>Pick a date</span>
                                        )}
                                    </Button>
                                </PopoverTrigger>
                                <PopoverContent className="w-auto p-0">
                                    <Calendar
                                        mode="single"
                                        selected={formData.purchaseDate}
                                        onSelect={(date) =>
                                            setFormData({ ...formData, purchaseDate: date })
                                        }
                                        initialFocus
                                    />
                                </PopoverContent>
                            </Popover>
                        </div>
                        <div className="space-y-2">
                            <Label>Portfolio Name</Label>
                            <Input
                                placeholder="e.g., Retirement"
                                value={formData.portfolioName}
                                onChange={(e) =>
                                    setFormData({ ...formData, portfolioName: e.target.value })
                                }
                            />
                        </div>
                        <div className="space-y-2">
                            <Label>Currency</Label>
                            <Select
                                value={formData.currency}
                                onValueChange={(value) =>
                                    setFormData({ ...formData, currency: value })
                                }
                            >
                                <SelectTrigger>
                                    <SelectValue placeholder="Select currency" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="USD">USD</SelectItem>
                                    <SelectItem value="EUR">EUR</SelectItem>
                                    <SelectItem value="GBP">GBP</SelectItem>
                                    <SelectItem value="INR">INR</SelectItem>
                                    <SelectItem value="JPY">JPY</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                        <div className="space-y-2">
                            <Label>Broker</Label>
                            <Input
                                placeholder="e.g., Robinhood"
                                value={formData.broker}
                                onChange={(e) =>
                                    setFormData({ ...formData, broker: e.target.value })
                                }
                            />
                        </div>
                        <div className="space-y-2">
                            <Label>Investment Type</Label>
                            <Select
                                value={formData.investmentType}
                                onValueChange={(value) =>
                                    setFormData({ ...formData, investmentType: value as AssetType })
                                }
                            >
                                <SelectTrigger>
                                    <SelectValue placeholder="Select type" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="Stock">Stock</SelectItem>
                                    <SelectItem value="Crypto">Crypto</SelectItem>
                                    <SelectItem value="Gold">Gold</SelectItem>
                                    <SelectItem value="Silver">Silver</SelectItem>
                                    <SelectItem value="Oil">Oil</SelectItem>
                                    <SelectItem value="Commodity">Commodity</SelectItem>
                                    <SelectItem value="Real Estate">Real Estate</SelectItem>
                                    <SelectItem value="Other">Other</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                    </div>

                    <div className="space-y-2">
                        <Label>Additional Information</Label>
                        <Textarea
                            placeholder="Any notes or details..."
                            value={formData.additionalInfo}
                            onChange={(e) =>
                                setFormData({ ...formData, additionalInfo: e.target.value })
                            }
                        />
                    </div>

                    <div className="space-y-2">
                        <Label>Attachments (PDF, CSV, Excel, TXT)</Label>
                        <div className="flex flex-wrap gap-2 mb-2">
                            {files.map((file, index) => (
                                <div
                                    key={index}
                                    className="flex items-center gap-2 bg-muted px-3 py-1 rounded-full text-sm"
                                >
                                    <FileText className="h-3 w-3" />
                                    <span className="truncate max-w-[150px]">{file.name}</span>
                                    <button
                                        type="button"
                                        onClick={() => removeFile(index)}
                                        className="text-muted-foreground hover:text-foreground"
                                    >
                                        <X className="h-3 w-3" />
                                    </button>
                                </div>
                            ))}
                        </div>
                        <div className="flex items-center gap-2">
                            <Button
                                type="button"
                                variant="outline"
                                onClick={() => fileInputRef.current?.click()}
                                className="w-full border-dashed"
                            >
                                <Upload className="h-4 w-4 mr-2" />
                                Upload Files
                            </Button>
                            <input
                                ref={fileInputRef}
                                type="file"
                                multiple
                                accept=".pdf,.csv,.xlsx,.xls,.txt"
                                onChange={handleFileChange}
                                className="hidden"
                            />
                        </div>
                    </div>

                    <div className="flex justify-end gap-2 pt-4">
                        <Button type="button" variant="ghost" onClick={onClose}>
                            Cancel
                        </Button>
                        <Button type="submit" disabled={isSubmitting}>
                            {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                            {initialData ? "Update Asset" : "Add Asset"}
                        </Button>
                    </div>
                </form>
            </div>
        </div>
    );
}
