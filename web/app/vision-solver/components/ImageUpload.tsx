"use client";

import { useCallback, useRef, useState } from "react";
import { Image as ImageIcon, Upload, Link as LinkIcon } from "lucide-react";
import { useTranslation } from "react-i18next";

interface ImageUploadProps {
  onImageUpload: (base64: string) => void;
  disabled?: boolean;
}

export function ImageUpload({ onImageUpload, disabled }: ImageUploadProps) {
  const { t } = useTranslation();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [showUrlInput, setShowUrlInput] = useState(false);
  const [urlValue, setUrlValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleFileSelect = useCallback(
    async (file: File) => {
      if (!file.type.startsWith("image/")) {
        alert(t("Please select an image file"));
        return;
      }

      // Check file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        alert(t("Image size must be less than 10MB"));
        return;
      }

      // Convert to base64
      const reader = new FileReader();
      reader.onload = (e) => {
        const base64 = e.target?.result as string;
        onImageUpload(base64);
      };
      reader.readAsDataURL(file);
    },
    [onImageUpload, t],
  );

  const handleFileInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) {
        handleFileSelect(file);
      }
      // Reset input
      e.target.value = "";
    },
    [handleFileSelect],
  );

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLButtonElement>) => {
      e.preventDefault();
      const file = e.dataTransfer.files[0];
      if (file) {
        handleFileSelect(file);
      }
    },
    [handleFileSelect],
  );

  const handlePaste = useCallback(
    (e: React.ClipboardEvent) => {
      const items = e.clipboardData.items;
      for (const item of items) {
        if (item.type.startsWith("image/")) {
          const file = item.getAsFile();
          if (file) {
            handleFileSelect(file);
          }
          break;
        }
      }
    },
    [handleFileSelect],
  );

  const handleUrlSubmit = useCallback(async () => {
    if (!urlValue.trim()) return;

    setIsLoading(true);
    try {
      const response = await fetch(urlValue);
      const blob = await response.blob();
      const reader = new FileReader();
      reader.onload = (e) => {
        const base64 = e.target?.result as string;
        onImageUpload(base64);
        setShowUrlInput(false);
        setUrlValue("");
      };
      reader.readAsDataURL(blob);
    } catch (error) {
      alert(t("Failed to load image from URL"));
    } finally {
      setIsLoading(false);
    }
  }, [urlValue, onImageUpload, t]);

  return (
    <div className="relative flex items-center gap-2">
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileInputChange}
        className="hidden"
      />

      {/* File Upload Button */}
      <button
        onClick={() => fileInputRef.current?.click()}
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
        onPaste={handlePaste}
        disabled={disabled}
        className="h-10 aspect-square bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg flex items-center justify-center hover:bg-slate-100 dark:hover:bg-slate-600 hover:border-indigo-300 dark:hover:border-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all group"
        title={t("Upload image (drag, paste, or click)")}
      >
        <Upload className="w-4 h-4 text-slate-400 dark:text-slate-500 group-hover:text-indigo-500 dark:group-hover:text-indigo-400 transition-colors" />
      </button>

      {/* URL Input Toggle Button */}
      <button
        onClick={() => setShowUrlInput(!showUrlInput)}
        disabled={disabled}
        className={`h-10 aspect-square border rounded-lg flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed transition-all group ${
          showUrlInput
            ? "bg-indigo-50 dark:bg-indigo-900/30 border-indigo-300 dark:border-indigo-600"
            : "bg-slate-50 dark:bg-slate-700 border-slate-200 dark:border-slate-600 hover:bg-slate-100 dark:hover:bg-slate-600 hover:border-indigo-300 dark:hover:border-indigo-500"
        }`}
        title={t("Enter image URL")}
      >
        <LinkIcon
          className={`w-4 h-4 transition-colors ${
            showUrlInput
              ? "text-indigo-500 dark:text-indigo-400"
              : "text-slate-400 dark:text-slate-500 group-hover:text-indigo-500 dark:group-hover:text-indigo-400"
          }`}
        />
      </button>

      {/* URL Input Popover */}
      {showUrlInput && (
        <div className="absolute bottom-full left-0 mb-2 w-80 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-600 rounded-lg shadow-lg p-3 z-10">
          <div className="flex gap-2">
            <input
              type="url"
              value={urlValue}
              onChange={(e) => setUrlValue(e.target.value)}
              placeholder={t("Enter image URL")}
              className="flex-1 px-3 py-2 text-sm bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
              onKeyDown={(e) => e.key === "Enter" && handleUrlSubmit()}
              autoFocus
            />
            <button
              onClick={handleUrlSubmit}
              disabled={isLoading || !urlValue.trim()}
              className="px-3 py-2 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors"
            >
              {isLoading ? "..." : t("Load")}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
