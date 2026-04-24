/**
 * Helpers for drag-and-drop document attachments in the chat composer.
 *
 * Must stay in sync with backend `deeptutor/utils/document_extractor.py`.
 */

import type { LucideIcon } from "lucide-react";
import {
  FilePlus2,
  FileSpreadsheet,
  FileText,
  FileType2,
  Presentation,
} from "lucide-react";

export const SUPPORTED_DOC_EXTS = [".pdf", ".docx", ".xlsx", ".pptx"] as const;

export const SUPPORTED_DOC_MIMES = new Set<string>([
  "application/pdf",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  "application/vnd.openxmlformats-officedocument.presentationml.presentation",
]);

export const MAX_ATTACHMENT_BYTES = 10 * 1024 * 1024;
export const MAX_TOTAL_ATTACHMENT_BYTES = 25 * 1024 * 1024;

/**
 * `accept` attribute for the chat composer's file picker. Mirrors the formats
 * the drag-and-drop / paste paths accept (see `classifyFile`). Listing both
 * MIME types and extensions improves cross-OS reliability — Windows in
 * particular often reports an empty `File.type` for OOXML files.
 */
export const ATTACHMENT_ACCEPT = [
  "image/*",
  ...SUPPORTED_DOC_EXTS,
  ...Array.from(SUPPORTED_DOC_MIMES),
].join(",");

export type FileKind = "image" | "doc";

function extOf(filename: string): string {
  const idx = filename.lastIndexOf(".");
  return idx >= 0 ? filename.slice(idx).toLowerCase() : "";
}

/**
 * Classify a dropped/pasted file. Returns null for unsupported types.
 *
 * Checks MIME first, falls back to extension because some OSes report an empty
 * `File.type` for .pptx / .xlsx.
 */
export function classifyFile(file: File): FileKind | null {
  if (file.type && file.type.startsWith("image/")) return "image";
  if (file.type && SUPPORTED_DOC_MIMES.has(file.type)) return "doc";
  const ext = extOf(file.name);
  if (ext && (SUPPORTED_DOC_EXTS as readonly string[]).includes(ext)) return "doc";
  // Some browsers report application/zip for unknown OOXML — fall back to extension above.
  if (!file.type && ext === "") return null;
  return null;
}

/**
 * Human-readable byte size: `1.2 MB`, `34.0 KB`.
 */
export function formatBytes(n: number): string {
  if (!Number.isFinite(n) || n < 0) return "";
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
  return `${(n / (1024 * 1024)).toFixed(1)} MB`;
}

export interface DocIconSpec {
  Icon: LucideIcon;
  tint: string; // tailwind class, e.g. "text-red-500/80"
  label: string; // e.g. "PDF"
}

export function docIconFor(filename: string): DocIconSpec {
  const ext = extOf(filename);
  switch (ext) {
    case ".pdf":
      return { Icon: FileType2, tint: "text-red-500/80", label: "PDF" };
    case ".docx":
      return { Icon: FileText, tint: "text-blue-500/80", label: "DOCX" };
    case ".xlsx":
      return { Icon: FileSpreadsheet, tint: "text-emerald-500/80", label: "XLSX" };
    case ".pptx":
      return { Icon: Presentation, tint: "text-orange-500/80", label: "PPTX" };
    default:
      return {
        Icon: FilePlus2,
        tint: "text-[var(--muted-foreground)]",
        label: ext ? ext.slice(1).toUpperCase() : "FILE",
      };
  }
}
