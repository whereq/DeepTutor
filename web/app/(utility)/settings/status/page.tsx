"use client";

import { useTranslation } from "react-i18next";

import {
  type ServiceName,
  getActiveModel,
  getActiveProfile,
  servicePendingApply,
  useSettings,
} from "@/components/settings/SettingsContext";
import {
  activeModelDetail,
  labelClass,
  statusDotClass,
  SettingsPageHeader,
} from "@/components/settings/shared";

const SERVICES: ServiceName[] = ["llm", "embedding", "search"];

function serviceLabel(service: ServiceName, t: (k: string) => string): string {
  if (service === "llm") return t("LLM");
  if (service === "embedding") return t("Embedding");
  return t("Search");
}

export default function StatusSettingsPage() {
  const { t } = useTranslation();
  const { status, catalog, draft, language } = useSettings();

  return (
    <div data-tour="tour-status">
      <SettingsPageHeader
        title={t("Status")}
        description={t(
          "Live state of the backend and the model services your configuration applies to.",
        )}
      />

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {/* Backend tile */}
        <div className="rounded-xl border border-[var(--border)]/60 bg-[var(--card)] px-4 py-4">
          <div className="flex items-center gap-2">
            <span
              className={`h-1.5 w-1.5 rounded-full ${statusDotClass(
                status?.backend.status === "online",
                false,
              )}`}
            />
            <span
              className={`${labelClass("md", language)} text-[var(--muted-foreground)]`}
            >
              {t("Backend")}
            </span>
          </div>
          <div className="mt-2 truncate text-[14px] font-medium text-[var(--foreground)]">
            {status?.backend.status === "online" ? t("Online") : t("Checking")}
          </div>
          <div className="mt-0.5 truncate text-[11px] text-[var(--muted-foreground)]">
            {(() => {
              const ts = status?.backend.timestamp;
              if (!ts) return "—";
              const parsed = new Date(ts);
              if (Number.isNaN(parsed.getTime())) return "";
              return parsed.toLocaleTimeString(
                language === "zh" ? "zh-CN" : "en-US",
                { hour: "2-digit", minute: "2-digit", second: "2-digit" },
              );
            })()}
          </div>
        </div>

        {SERVICES.map((service) => {
          const profile = getActiveProfile(draft, service);
          const model = getActiveModel(draft, service);
          const serviceStatus =
            service === "llm"
              ? status?.llm
              : service === "embedding"
                ? status?.embeddings
                : status?.search;
          const runtimeModel =
            service === "llm"
              ? status?.llm.model
              : service === "embedding"
                ? status?.embeddings.model
                : undefined;
          const configured =
            service === "search"
              ? Boolean(profile?.provider || status?.search.provider)
              : Boolean(model?.model || runtimeModel);
          const pendingApply = servicePendingApply(catalog, draft, service);
          const detail = activeModelDetail(profile, model, service, t);
          const profileName = profile?.name || t("No profile");

          return (
            <div
              key={service}
              className="rounded-xl border border-[var(--border)]/60 bg-[var(--card)] px-4 py-4"
            >
              <div className="flex items-center gap-2">
                <span
                  className={`h-1.5 w-1.5 rounded-full ${statusDotClass(
                    configured,
                    Boolean(serviceStatus?.error),
                  )}`}
                />
                <span
                  className={`${labelClass("md", language)} text-[var(--muted-foreground)]`}
                >
                  {serviceLabel(service, t)}
                </span>
                {pendingApply && (
                  <span className="ml-auto text-[10px] font-medium text-amber-600 dark:text-amber-400">
                    {t("Pending")}
                  </span>
                )}
              </div>
              <div className="mt-2 truncate text-[14px] font-medium text-[var(--foreground)]">
                {detail}
              </div>
              <div className="mt-0.5 truncate text-[11px] text-[var(--muted-foreground)]">
                {profileName}
              </div>
              {serviceStatus?.error && (
                <p
                  className="mt-2 truncate text-[11px] text-red-500"
                  title={serviceStatus.error}
                >
                  {serviceStatus.error}
                </p>
              )}
            </div>
          );
        })}
      </div>

      <p className="mt-6 text-[11.5px] leading-relaxed text-[var(--muted-foreground)]/70">
        {t(
          "Status reflects the runtime values after the last Apply. Draft changes only take effect once applied.",
        )}
      </p>
    </div>
  );
}
