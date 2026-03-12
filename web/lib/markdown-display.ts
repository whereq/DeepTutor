"use client";

const ZERO_WIDTH_REGEX = /[\u200B-\u200D\uFEFF]/g;
const EMPTY_DETAILS_REGEX =
  /<details(?:\s[^>]*)?>\s*(<summary(?:\s[^>]*)?>\s*(?:&nbsp;|\s|<br\s*\/?>)*\s*<\/summary>\s*)?<\/details>/gi;
const EMPTY_SUMMARY_REGEX =
  /<summary(?:\s[^>]*)?>\s*(?:&nbsp;|\s|<br\s*\/?>)*\s*<\/summary>/gi;
const EMPTY_FENCED_CODE_BLOCK_REGEX = /```[^\n`]*\n?\s*```/g;
const EMPTY_HTML_BLOCK_REGEX =
  /<(p|div|section|article|aside|blockquote)(?:\s[^>]*)?>\s*(?:&nbsp;|\s|<br\s*\/?>)*\s*<\/\1>/gi;
const HTML_TABLE_REGEX = /<table(?:\s[^>]*)?>[\s\S]*?<\/table>/gi;

function stripInvisibleCharacters(value: string): string {
  return value.replace(ZERO_WIDTH_REGEX, "");
}

function stripDisplaySyntax(value: string): string {
  return stripInvisibleCharacters(String(value))
    .replace(/&nbsp;/gi, " ")
    .replace(/<br\s*\/?>/gi, " ")
    .replace(/<[^>]+>/g, "")
    .replace(/!\[(.*?)\]\([^)]+\)/g, "$1")
    .replace(/\[(.*?)\]\([^)]+\)/g, "$1")
    .replace(/[`*_~]/g, "")
    .trim();
}

function splitMarkdownTableCells(line: string): string[] {
  const trimmed = line.trim().replace(/^\|/, "").replace(/\|$/, "");
  if (!trimmed) return [""];
  return trimmed.split("|");
}

function isMarkdownTableSeparator(line: string): boolean {
  const trimmed = line.trim();
  if (!trimmed.includes("|")) return false;
  const cells = splitMarkdownTableCells(trimmed);
  return cells.length > 0 && cells.every((cell) => /^:?-{3,}:?$/.test(cell.trim()));
}

function isMarkdownTableStart(lines: string[], index: number): boolean {
  if (index + 1 >= lines.length) return false;

  const header = lines[index]?.trim() || "";
  const separator = lines[index + 1]?.trim() || "";
  if (!header || !separator || !header.includes("|") || !isMarkdownTableSeparator(separator)) {
    return false;
  }

  return splitMarkdownTableCells(header).length === splitMarkdownTableCells(separator).length;
}

function isMarkdownTableBodyRow(line: string, columnCount: number): boolean {
  const trimmed = line.trim();
  if (!trimmed || !trimmed.includes("|")) return false;
  return splitMarkdownTableCells(trimmed).length === columnCount;
}

function isEmptyMarkdownTable(lines: string[]): boolean {
  return lines
    .filter((_, index) => index !== 1)
    .every((line) => splitMarkdownTableCells(line).every((cell) => stripDisplaySyntax(cell).length === 0));
}

function removeEmptyMarkdownTables(content: string): string {
  const lines = content.split("\n");
  const cleaned: string[] = [];

  for (let index = 0; index < lines.length;) {
    if (!isMarkdownTableStart(lines, index)) {
      cleaned.push(lines[index]);
      index += 1;
      continue;
    }

    const columnCount = splitMarkdownTableCells(lines[index]).length;
    let end = index + 2;
    while (end < lines.length && isMarkdownTableBodyRow(lines[end], columnCount)) {
      end += 1;
    }

    const tableLines = lines.slice(index, end);
    if (!isEmptyMarkdownTable(tableLines)) {
      cleaned.push(...tableLines);
    }
    index = end;
  }

  return cleaned.join("\n");
}

function removeEmptyHtmlTables(content: string): string {
  return content.replace(HTML_TABLE_REGEX, (block) => (stripDisplaySyntax(block) ? block : ""));
}

export function normalizeMarkdownForDisplay(content: string): string {
  if (!content) return "";

  const normalized = stripInvisibleCharacters(String(content))
    .replace(/\r\n/g, "\n")
    .replace(EMPTY_DETAILS_REGEX, "")
    .replace(EMPTY_SUMMARY_REGEX, "")
    .replace(EMPTY_HTML_BLOCK_REGEX, "")
    .replace(/\n{3,}/g, "\n\n")
    .replace(/^\n+|\n+$/g, "");

  return removeEmptyMarkdownTables(removeEmptyHtmlTables(normalized)).replace(/\n{3,}/g, "\n\n");
}

export function hasVisibleMarkdownContent(content: string): boolean {
  const normalized = normalizeMarkdownForDisplay(content);
  if (!normalized.trim()) return false;

  const withoutEmptyBlocks = normalized
    .replace(EMPTY_FENCED_CODE_BLOCK_REGEX, "")
    .replace(/<[^>]+>/g, "")
    .replace(/\[(.*?)\]\([^)]+\)/g, "$1")
    .replace(/!\[(.*?)\]\([^)]+\)/g, "$1")
    .replace(/^[\s>*\-+|#`]+$/gm, "");

  return stripInvisibleCharacters(withoutEmptyBlocks).trim().length > 0;
}
