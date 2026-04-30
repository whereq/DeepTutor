export type MessageContentItem = {
  type: string;
  text?: string;
  url?: string;
  alt?: string;
};

export type RawMessageContent =
  | string
  | MessageContentItem[]
  | null
  | undefined
  | unknown;

export function normalizeMessageContent(content: RawMessageContent): string {
  if (content == null) return "";
  if (typeof content === "string") return content;
  if (Array.isArray(content)) {
    return content
      .map((item) => {
        if (!item || typeof item !== "object") return String(item);
        if (item.type === "image" || item.type === "image_url") {
          return item.alt || item.text || "[image]";
        }
        return item.text ?? String(item);
      })
      .filter(Boolean)
      .join(" ");
  }
  return String(content);
}

export function truncateText(text: string, maxLength: number = 100): string {
  if (!text) return "";
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + "…";
}
