import { useState } from "react";
import { Settings, Moon, Sun, Monitor, Pencil, Check, X, Briefcase, LayoutDashboard, FileDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import { Link } from "react-router-dom";

type Theme = "light" | "dark" | "system";

interface ChatHeaderProps {
  title: string;
  theme: Theme;
  onThemeChange: (theme: Theme) => void;
  onRename: (title: string) => void;
  onToggleAssets: () => void;
  onExport: () => void;
  hasMessages: boolean;
}

export function ChatHeader({
  title,
  theme,
  onThemeChange,
  onRename,
  onToggleAssets,
  onExport,
  hasMessages,
}: ChatHeaderProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(title);

  const handleStartEdit = () => {
    setEditValue(title);
    setIsEditing(true);
  };

  const handleSave = () => {
    if (editValue.trim()) {
      onRename(editValue.trim());
    }
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditValue(title);
    setIsEditing(false);
  };

  const themeIcon = {
    light: Sun,
    dark: Moon,
    system: Monitor,
  };

  const ThemeIcon = themeIcon[theme];

  return (
    <header className="h-14 border-b border-border bg-background px-4 flex items-center justify-between">
      {/* Left: App title and chat name */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={onToggleAssets}
            className="text-foreground hover:bg-accent"
            title="Asset Manager"
          >
            <Briefcase className="h-5 w-5" />
          </Button>
          <h1 className="font-semibold text-lg text-foreground hidden sm:block">
            Work-o-pilot
          </h1>
        </div>
        <span className="text-muted-foreground hidden sm:block">/</span>

        {isEditing ? (
          <div className="flex items-center gap-1">
            <Input
              value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleSave();
                if (e.key === "Escape") handleCancel();
              }}
              autoFocus
              className="h-8 w-48"
            />
            <Button variant="ghost" size="icon" className="h-7 w-7" onClick={handleSave}>
              <Check className="h-3 w-3" />
            </Button>
            <Button variant="ghost" size="icon" className="h-7 w-7" onClick={handleCancel}>
              <X className="h-3 w-3" />
            </Button>
          </div>
        ) : (
          <button
            className="flex items-center gap-2 text-foreground hover:text-muted-foreground transition-colors group"
            onClick={handleStartEdit}
          >
            <span className="truncate max-w-[200px]">{title}</span>
            <Pencil className="h-3 w-3 opacity-0 group-hover:opacity-100 transition-opacity" />
          </button>
        )}
      </div>

      {/* Right: Settings */}
      <div className="flex items-center gap-2">
        {hasMessages && (
          <Button
            variant="ghost"
            size="icon"
            onClick={onExport}
            className="h-9 w-9"
            title="Export Chat"
          >
            <FileDown className="h-4 w-4" />
          </Button>
        )}

        <Button variant="ghost" size="icon" asChild className="hidden sm:flex">
          <Link to="/assets" title="View Assets">
            <LayoutDashboard className="h-4 w-4" />
          </Link>
        </Button>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="h-9 w-9">
              <ThemeIcon className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-40">
            <DropdownMenuLabel>Theme</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              onClick={() => onThemeChange("light")}
              className={cn(theme === "light" && "bg-accent")}
            >
              <Sun className="h-4 w-4 mr-2" />
              Light
            </DropdownMenuItem>
            <DropdownMenuItem
              onClick={() => onThemeChange("dark")}
              className={cn(theme === "dark" && "bg-accent")}
            >
              <Moon className="h-4 w-4 mr-2" />
              Dark
            </DropdownMenuItem>
            <DropdownMenuItem
              onClick={() => onThemeChange("system")}
              className={cn(theme === "system" && "bg-accent")}
            >
              <Monitor className="h-4 w-4 mr-2" />
              System
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        <Button variant="ghost" size="icon" className="h-9 w-9">
          <Settings className="h-4 w-4" />
        </Button>
      </div>
    </header>
  );
}
