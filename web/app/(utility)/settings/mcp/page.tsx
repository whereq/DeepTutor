"use client";

import { Plug } from "lucide-react";
import { useTranslation } from "react-i18next";

import { SettingsPageHeader } from "@/components/settings/shared";

export default function McpSettingsPage() {
  const { t } = useTranslation();

  return (
    <div data-tour="tour-mcp">
      <SettingsPageHeader
        title={t("MCP servers")}
        description={t(
          "Connect external MCP (Model Context Protocol) servers to extend the agent's capabilities.",
        )}
      />

      <div className="flex flex-col items-center justify-center gap-3 rounded-xl border border-dashed border-[var(--border)]/70 bg-[var(--card)]/30 px-6 py-16 text-center">
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[var(--muted)]/60">
          <Plug className="h-4 w-4 text-[var(--muted-foreground)]" />
        </div>
        <div className="text-[14px] font-medium text-[var(--foreground)]">
          {t("MCP server support is coming soon")}
        </div>
        <p className="max-w-md text-[12.5px] leading-relaxed text-[var(--muted-foreground)]">
          {t(
            "We're working on a way to register and authenticate MCP servers from this page so the chat agent can call tools they expose. Until then, this section is reserved as a placeholder.",
          )}
        </p>
      </div>
    </div>
  );
}
