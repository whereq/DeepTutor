"use client";

import { useEffect, useMemo, useState } from "react";
import {
  Brain,
  Database,
  Globe,
  Loader2,
  Search,
  Settings as SettingsIcon,
  Sparkles,
  Volume2,
} from "lucide-react";
import { apiUrl } from "@/lib/api";

type ConfigType = "llm" | "embedding" | "tts" | "search";

interface StoredConfig {
  id: string;
  name: string;
  provider: string;
  model?: string;
  base_url?: string | { use_env: string };
  api_key?: string | { use_env: string };
  voice?: string;
  dimensions?: number;
  is_active?: boolean;
}

interface ConfigSectionProps {
  type: ConfigType;
  title: string;
  icon: React.ReactNode;
  fields: Array<"name" | "provider" | "model" | "base_url" | "api_key" | "voice" | "dimensions">;
}

const THEME_KEY = "deeptutor-theme";
const LANGUAGE_KEY = "deeptutor-language";

function ConfigSection({ type, title, icon, fields }: ConfigSectionProps) {
  const [configs, setConfigs] = useState<StoredConfig[]>([]);
  const [providerOptions, setProviderOptions] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState<Record<string, string>>({
    name: "",
    provider: "openai",
    model: "",
    base_url: "",
    api_key: "",
    voice: "alloy",
    dimensions: "3072",
  });

  const load = async () => {
    setLoading(true);
    try {
      const [configsRes, providersRes] = await Promise.all([
        fetch(apiUrl(`/api/v1/config/${type}`)),
        fetch(apiUrl(`/api/v1/config/providers/${type}`)),
      ]);
      const data = await configsRes.json();
      const providersData = await providersRes.json();
      setConfigs(data.configs || []);
      setProviderOptions(Array.isArray(providersData.providers) ? providersData.providers : []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [type]);

  const createConfig = async () => {
    setSubmitting(true);
    try {
      const payload: Record<string, unknown> = {};
      for (const field of fields) {
        if (field === "dimensions") {
          payload[field] = Number(form[field] || "3072");
        } else {
          payload[field] = form[field];
        }
      }

      const res = await fetch(apiUrl(`/api/v1/config/${type}`), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || `Failed to create ${type} config`);
      }

      setForm((prev) => ({
        ...prev,
        name: "",
        model: "",
        base_url: "",
        api_key: "",
      }));
      await load();
    } finally {
      setSubmitting(false);
    }
  };

  const activateConfig = async (configId: string) => {
    await fetch(apiUrl(`/api/v1/config/${type}/${configId}/active`), {
      method: "POST",
    });
    await load();
  };

  return (
    <section className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-5 shadow-sm">
      <div className="mb-4 flex items-center gap-2.5">
        <div className="rounded-lg bg-[var(--muted)] p-2 text-[var(--muted-foreground)]">
          {icon}
        </div>
        <div>
          <h2 className="text-[14px] font-semibold text-[var(--foreground)]">{title}</h2>
          <p className="text-[12px] text-[var(--muted-foreground)]">
            Manage saved {type} configurations.
          </p>
        </div>
      </div>

      <div className="grid gap-2.5 md:grid-cols-2 xl:grid-cols-3">
        {fields.includes("name") && (
          <input
            value={form.name}
            onChange={(event) => setForm((prev) => ({ ...prev, name: event.target.value }))}
            placeholder="Name"
            className="rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-2 text-[13px] outline-none transition-colors focus:border-[var(--foreground)]/25"
          />
        )}
        {fields.includes("provider") && (
          providerOptions.length > 0 ? (
            <select
              value={form.provider}
              onChange={(event) =>
                setForm((prev) => ({ ...prev, provider: event.target.value }))
              }
              className="rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-2 text-[13px] outline-none transition-colors focus:border-[var(--foreground)]/25"
            >
              {providerOptions.map((provider) => (
                <option key={provider} value={provider}>
                  {provider}
                </option>
              ))}
            </select>
          ) : (
            <input
              value={form.provider}
              onChange={(event) =>
                setForm((prev) => ({ ...prev, provider: event.target.value }))
              }
              placeholder="Provider"
              className="rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-2 text-[13px] outline-none transition-colors focus:border-[var(--foreground)]/25"
            />
          )
        )}
        {fields.includes("model") && (
          <input
            value={form.model}
            onChange={(event) => setForm((prev) => ({ ...prev, model: event.target.value }))}
            placeholder="Model"
            className="rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-2 text-[13px] outline-none transition-colors focus:border-[var(--foreground)]/25"
          />
        )}
        {fields.includes("base_url") && (
          <input
            value={form.base_url}
            onChange={(event) =>
              setForm((prev) => ({ ...prev, base_url: event.target.value }))
            }
            placeholder="Base URL"
            className="rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-2 text-[13px] outline-none transition-colors focus:border-[var(--foreground)]/25"
          />
        )}
        {fields.includes("api_key") && (
          <input
            value={form.api_key}
            onChange={(event) =>
              setForm((prev) => ({ ...prev, api_key: event.target.value }))
            }
            placeholder="API Key"
            className="rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-2 text-[13px] outline-none transition-colors focus:border-[var(--foreground)]/25"
          />
        )}
        {fields.includes("voice") && (
          <input
            value={form.voice}
            onChange={(event) => setForm((prev) => ({ ...prev, voice: event.target.value }))}
            placeholder="Voice"
            className="rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-2 text-[13px] outline-none transition-colors focus:border-[var(--foreground)]/25"
          />
        )}
        {fields.includes("dimensions") && (
          <input
            value={form.dimensions}
            onChange={(event) =>
              setForm((prev) => ({ ...prev, dimensions: event.target.value }))
            }
            placeholder="Dimensions"
            className="rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-2 text-[13px] outline-none transition-colors focus:border-[var(--foreground)]/25"
          />
        )}
      </div>

      <div className="mt-3">
        <button
          onClick={createConfig}
          disabled={submitting || !form.name || !form.provider}
          className="rounded-lg bg-[var(--primary)] px-3.5 py-1.5 text-[13px] font-medium text-[var(--primary-foreground)] disabled:cursor-not-allowed disabled:opacity-40"
        >
          {submitting ? "Saving..." : "Add configuration"}
        </button>
      </div>

      <div className="mt-5 space-y-2">
        {loading ? (
          <div className="flex items-center gap-2 text-[13px] text-[var(--muted-foreground)]">
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
            Loading...
          </div>
        ) : configs.length ? (
          configs.map((config) => (
            <div
              key={config.id}
              className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-2.5"
            >
              <div className="min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-[13px] font-medium text-[var(--foreground)]">
                    {config.name}
                  </span>
                  {config.is_active && (
                    <span className="rounded-md bg-[var(--muted)] px-1.5 py-0.5 text-[10px] font-medium text-[var(--muted-foreground)]">
                      Active
                    </span>
                  )}
                </div>
                <div className="mt-0.5 text-[11px] text-[var(--muted-foreground)]">
                  {config.provider}
                  {config.model ? ` · ${config.model}` : ""}
                </div>
              </div>
              {!config.is_active && (
                <button
                  onClick={() => activateConfig(config.id)}
                  className="rounded-md border border-[var(--border)] px-2.5 py-1 text-[12px] text-[var(--foreground)] transition-colors hover:bg-[var(--muted)]"
                >
                  Set active
                </button>
              )}
            </div>
          ))
        ) : (
          <div className="rounded-lg border border-dashed border-[var(--border)] px-4 py-8 text-center text-[13px] text-[var(--muted-foreground)]">
            No saved configurations yet.
          </div>
        )}
      </div>
    </section>
  );
}

export default function SettingsPage() {
  const [theme, setTheme] = useState<"light" | "dark">(() => {
    if (typeof window === "undefined") return "light";
    try {
      const storedTheme = window.localStorage.getItem(THEME_KEY);
      return storedTheme === "dark" || storedTheme === "light" ? storedTheme : "light";
    } catch {
      return "light";
    }
  });
  const [language, setLanguage] = useState<"en" | "zh">(() => {
    if (typeof window === "undefined") return "en";
    try {
      const storedLanguage = window.localStorage.getItem(LANGUAGE_KEY);
      return storedLanguage === "zh" || storedLanguage === "en" ? storedLanguage : "en";
    } catch {
      return "en";
    }
  });

  const updateTheme = async (nextTheme: "light" | "dark") => {
    setTheme(nextTheme);
    document.documentElement.classList.toggle("dark", nextTheme === "dark");
    try {
      window.localStorage.setItem(THEME_KEY, nextTheme);
    } catch {}
    await fetch(apiUrl("/api/v1/settings/theme"), {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ theme: nextTheme }),
    });
  };

  const updateLanguage = async (nextLanguage: "en" | "zh") => {
    setLanguage(nextLanguage);
    try {
      window.localStorage.setItem(LANGUAGE_KEY, nextLanguage);
    } catch {}
    await fetch(apiUrl("/api/v1/settings/language"), {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ language: nextLanguage }),
    });
    window.location.reload();
  };

  const sections = useMemo<ConfigSectionProps[]>(
    () => [
      {
        type: "llm",
        title: "LLM",
        icon: <Brain className="h-4 w-4" />,
        fields: ["name", "provider", "model", "base_url", "api_key"],
      },
      {
        type: "embedding",
        title: "Embedding",
        icon: <Database className="h-4 w-4" />,
        fields: ["name", "provider", "model", "base_url", "api_key", "dimensions"],
      },
      {
        type: "tts",
        title: "TTS",
        icon: <Volume2 className="h-4 w-4" />,
        fields: ["name", "provider", "model", "base_url", "api_key", "voice"],
      },
      {
        type: "search",
        title: "Search",
        icon: <Search className="h-4 w-4" />,
        fields: ["name", "provider", "api_key"],
      },
    ],
    [],
  );

  return (
    <div className="min-h-screen bg-[var(--background)]">
      <div className="mx-auto max-w-5xl px-6 py-8">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold tracking-tight text-[var(--foreground)]">
            Settings
          </h1>
          <p className="mt-1 text-[13px] text-[var(--muted-foreground)]">
            Configure API keys, active providers, theme, and language.
          </p>
        </div>

        {/* Interface section */}
        <section className="mb-5 rounded-xl border border-[var(--border)] bg-[var(--card)] p-5 shadow-sm">
          <div className="mb-4 flex items-center gap-2.5">
            <div className="rounded-lg bg-[var(--muted)] p-2 text-[var(--muted-foreground)]">
              <Sparkles className="h-4 w-4" />
            </div>
            <div>
              <h2 className="text-[14px] font-semibold text-[var(--foreground)]">
                Interface
              </h2>
              <p className="text-[12px] text-[var(--muted-foreground)]">
                Personalize the look and language of DeepTutor.
              </p>
            </div>
          </div>

          <div className="grid gap-3 md:grid-cols-2">
            <div className="rounded-lg border border-[var(--border)] bg-[var(--background)] p-3.5">
              <div className="mb-2.5 text-[13px] font-medium text-[var(--foreground)]">
                Theme
              </div>
              <div className="flex gap-1.5">
                {(["light", "dark"] as const).map((value) => (
                  <button
                    key={value}
                    onClick={() => updateTheme(value)}
                    className={`rounded-md px-3 py-1.5 text-[12px] font-medium transition-all ${
                      theme === value
                        ? "bg-[var(--primary)] text-[var(--primary-foreground)]"
                        : "border border-[var(--border)] text-[var(--foreground)] hover:bg-[var(--muted)]"
                    }`}
                  >
                    {value === "light" ? "Light" : "Dark"}
                  </button>
                ))}
              </div>
            </div>

            <div className="rounded-lg border border-[var(--border)] bg-[var(--background)] p-3.5">
              <div className="mb-2.5 flex items-center gap-1.5 text-[13px] font-medium text-[var(--foreground)]">
                <Globe className="h-3.5 w-3.5" />
                Language
              </div>
              <div className="flex gap-1.5">
                {(["en", "zh"] as const).map((value) => (
                  <button
                    key={value}
                    onClick={() => updateLanguage(value)}
                    className={`rounded-md px-3 py-1.5 text-[12px] font-medium transition-all ${
                      language === value
                        ? "bg-[var(--primary)] text-[var(--primary-foreground)]"
                        : "border border-[var(--border)] text-[var(--foreground)] hover:bg-[var(--muted)]"
                    }`}
                  >
                    {value === "en" ? "English" : "中文"}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </section>

        <div className="space-y-5">
          {sections.map((section) => (
            <ConfigSection key={section.type} {...section} />
          ))}
        </div>
      </div>
    </div>
  );
}
