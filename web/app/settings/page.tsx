"use client";

import { useState, useEffect } from "react";
import {
  Settings as SettingsIcon,
  Brain,
  Database,
  Volume2,
  Search,
  Plus,
  Trash2,
  Check,
  Loader2,
  AlertCircle,
  Server,
  Eye,
  EyeOff,
  RefreshCw,
  ChevronDown,
  Sun,
  Moon,
  Globe,
  Pencil,
  TestTube,
} from "lucide-react";
import { apiUrl } from "@/lib/api";
import { useGlobal } from "@/context/GlobalContext";
import { getTranslation } from "@/lib/i18n";

// Language options
const LANGUAGE_OPTIONS = [
  { value: "en" as const, label: "English" },
  { value: "zh" as const, label: "中文" },
];

// Types
interface ConfigItem {
  id: string;
  name: string;
  provider: string;
  base_url?: string;
  api_key?: string;
  model?: string;
  dimensions?: number;
  voice?: string;
  api_version?: string;
  is_default?: boolean;
  is_active?: boolean;
}

interface ConfigStatus {
  configured: boolean;
  active_config_id: string;
  active_config_name: string;
  model: string | null;
  provider: string | null;
  env_configured: Record<string, boolean>;
  total_configs: number;
}

interface FullStatus {
  llm: ConfigStatus;
  embedding: ConfigStatus;
  tts: ConfigStatus;
  search: ConfigStatus;
}

interface PortsInfo {
  backend_port: number;
  frontend_port: number;
}

type ConfigType = "llm" | "embedding" | "tts" | "search";
type TabType = "overview" | ConfigType;

// Provider options
// Provider options - Cloud services first, then local deployments
const PROVIDER_OPTIONS: Record<ConfigType, string[]> = {
  llm: [
    // Cloud providers
    "openai",
    "anthropic",
    "azure_openai",
    "deepseek",
    "openrouter",
    // Local providers
    "ollama",
    "lm_studio",
    "vllm",
    "llama_cpp",
  ],
  embedding: [
    // Cloud providers
    "openai",
    "azure_openai",
    "jina",
    "cohere",
    "huggingface",
    "google",
    // Local providers
    "ollama",
    "lm_studio",
  ],
  tts: ["openai", "azure_openai"],
  search: ["perplexity", "tavily", "exa", "jina", "serper", "baidu"],
};

// Local providers that don't require API keys
const LOCAL_PROVIDERS = ["ollama", "lm_studio", "vllm", "llama_cpp"];

// Default base URLs for local providers
const LOCAL_PROVIDER_URLS: Record<string, string> = {
  ollama: "http://localhost:11434/v1",
  lm_studio: "http://localhost:1234/v1",
  vllm: "http://localhost:8000/v1",
  llama_cpp: "http://localhost:8080/v1",
};

// Voice options for TTS
const VOICE_OPTIONS = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"];

export default function SettingsPage() {
  const { uiSettings, updateTheme, updateLanguage } = useGlobal();
  const t = (key: string) => getTranslation(uiSettings.language, key);

  const [activeTab, setActiveTab] = useState<TabType>("overview");
  const [status, setStatus] = useState<FullStatus | null>(null);
  const [ports, setPorts] = useState<PortsInfo | null>(null);
  const [loading, setLoading] = useState(true);

  // Load initial data
  useEffect(() => {
    loadStatus();
    loadPorts();
  }, []);

  const loadStatus = async () => {
    try {
      const res = await fetch(apiUrl("/api/v1/config/status"));
      if (res.ok) {
        const data = await res.json();
        setStatus(data);
      }
    } catch (e) {
      console.error("Failed to load config status:", e);
    } finally {
      setLoading(false);
    }
  };

  const loadPorts = async () => {
    try {
      const res = await fetch(apiUrl("/api/v1/config/ports"));
      if (res.ok) {
        const data = await res.json();
        setPorts(data);
      }
    } catch (e) {
      console.error("Failed to load ports:", e);
    }
  };

  const tabs: { id: TabType; label: string; icon: React.ReactNode }[] = [
    {
      id: "overview",
      label: "Overview",
      icon: <SettingsIcon className="w-4 h-4" />,
    },
    { id: "llm", label: "LLM", icon: <Brain className="w-4 h-4" /> },
    {
      id: "embedding",
      label: "Embedding",
      icon: <Database className="w-4 h-4" />,
    },
    { id: "tts", label: "TTS", icon: <Volume2 className="w-4 h-4" /> },
    { id: "search", label: "Search", icon: <Search className="w-4 h-4" /> },
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-900 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900">
      <div className="max-w-6xl mx-auto p-6">
        {/* Header */}
        <div className="flex items-center gap-3 mb-6">
          <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-xl">
            <SettingsIcon className="w-6 h-6 text-blue-600 dark:text-blue-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
              {uiSettings.language === "zh" ? "设置" : "Settings"}
            </h1>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              {uiSettings.language === "zh"
                ? "配置 AI 服务和界面偏好"
                : "Configure your AI services and preferences"}
            </p>
          </div>
        </div>

        {/* General Settings - Theme & Language */}
        <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-4 mb-6">
          <div className="flex flex-wrap items-center gap-6">
            {/* Theme Toggle */}
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400">
                {uiSettings.theme === "dark" ? (
                  <Moon className="w-4 h-4" />
                ) : (
                  <Sun className="w-4 h-4" />
                )}
                <span>{uiSettings.language === "zh" ? "主题" : "Theme"}</span>
              </div>
              <div className="flex p-1 bg-slate-100 dark:bg-slate-700 rounded-lg">
                <button
                  onClick={() => updateTheme("light")}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm transition-all ${
                    uiSettings.theme === "light"
                      ? "bg-white dark:bg-slate-600 text-slate-900 dark:text-slate-100 shadow-sm"
                      : "text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300"
                  }`}
                >
                  <Sun className="w-3.5 h-3.5" />
                  {uiSettings.language === "zh" ? "浅色" : "Light"}
                </button>
                <button
                  onClick={() => updateTheme("dark")}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm transition-all ${
                    uiSettings.theme === "dark"
                      ? "bg-white dark:bg-slate-600 text-slate-900 dark:text-slate-100 shadow-sm"
                      : "text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300"
                  }`}
                >
                  <Moon className="w-3.5 h-3.5" />
                  {uiSettings.language === "zh" ? "深色" : "Dark"}
                </button>
              </div>
            </div>

            {/* Separator */}
            <div className="h-8 w-px bg-slate-200 dark:bg-slate-700 hidden sm:block" />

            {/* Language Selector */}
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400">
                <Globe className="w-4 h-4" />
                <span>
                  {uiSettings.language === "zh" ? "语言" : "Language"}
                </span>
              </div>
              <div className="flex p-1 bg-slate-100 dark:bg-slate-700 rounded-lg">
                {LANGUAGE_OPTIONS.map((lang) => (
                  <button
                    key={lang.value}
                    onClick={() => updateLanguage(lang.value)}
                    className={`px-3 py-1.5 rounded-md text-sm transition-all ${
                      uiSettings.language === lang.value
                        ? "bg-white dark:bg-slate-600 text-slate-900 dark:text-slate-100 shadow-sm"
                        : "text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300"
                    }`}
                  >
                    {lang.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-1 p-1 bg-slate-100 dark:bg-slate-800 rounded-xl mb-6">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all ${
                activeTab === tab.id
                  ? "bg-white dark:bg-slate-700 text-blue-600 dark:text-blue-400 shadow-sm"
                  : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200"
              }`}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 overflow-hidden">
          {activeTab === "overview" && (
            <OverviewTab status={status} ports={ports} onRefresh={loadStatus} />
          )}
          {activeTab === "llm" && (
            <ConfigTab
              configType="llm"
              title="LLM Configuration"
              description="Configure language model providers"
              onUpdate={loadStatus}
            />
          )}
          {activeTab === "embedding" && (
            <ConfigTab
              configType="embedding"
              title="Embedding Configuration"
              description="Configure embedding model providers"
              onUpdate={loadStatus}
              showDimensions
            />
          )}
          {activeTab === "tts" && (
            <ConfigTab
              configType="tts"
              title="TTS Configuration"
              description="Configure text-to-speech providers"
              onUpdate={loadStatus}
              showVoice
            />
          )}
          {activeTab === "search" && (
            <ConfigTab
              configType="search"
              title="Search Configuration"
              description="Configure web search providers"
              onUpdate={loadStatus}
              isSearchConfig
            />
          )}
        </div>
      </div>
    </div>
  );
}

// Overview Tab Component
function OverviewTab({
  status,
  ports,
  onRefresh,
}: {
  status: FullStatus | null;
  ports: PortsInfo | null;
  onRefresh: () => void;
}) {
  const services = [
    { key: "llm" as const, label: "LLM", icon: Brain, color: "purple" },
    {
      key: "embedding" as const,
      label: "Embedding",
      icon: Database,
      color: "indigo",
    },
    { key: "tts" as const, label: "TTS", icon: Volume2, color: "emerald" },
    { key: "search" as const, label: "Search", icon: Search, color: "amber" },
  ];

  return (
    <div className="p-6 space-y-6">
      {/* Refresh Button */}
      <div className="flex justify-end">
        <button
          onClick={onRefresh}
          className="flex items-center gap-2 px-3 py-1.5 text-sm text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>

      {/* Service Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {services.map((service) => {
          const s = status?.[service.key];
          const Icon = service.icon;
          const isConfigured = s?.configured;

          return (
            <div
              key={service.key}
              className={`p-4 rounded-xl border ${
                isConfigured
                  ? "border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-900/20"
                  : "border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50"
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div
                    className={`p-2 rounded-lg ${
                      isConfigured
                        ? "bg-green-100 dark:bg-green-800/50"
                        : "bg-slate-100 dark:bg-slate-700"
                    }`}
                  >
                    <Icon
                      className={`w-5 h-5 ${
                        isConfigured
                          ? "text-green-600 dark:text-green-400"
                          : "text-slate-400"
                      }`}
                    />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-900 dark:text-slate-100">
                      {service.label}
                    </h3>
                    <p className="text-sm text-slate-500 dark:text-slate-400">
                      {s?.active_config_name || "Not configured"}
                    </p>
                  </div>
                </div>
                {isConfigured ? (
                  <Check className="w-5 h-5 text-green-500" />
                ) : (
                  <AlertCircle className="w-5 h-5 text-slate-400" />
                )}
              </div>
              {s?.model && (
                <div className="mt-3 pt-3 border-t border-slate-200 dark:border-slate-700">
                  <div className="flex items-center gap-2 text-sm">
                    <span className="text-slate-500 dark:text-slate-400">
                      Model:
                    </span>
                    <span className="font-mono text-slate-700 dark:text-slate-300">
                      {s.model}
                    </span>
                  </div>
                  {s.provider && (
                    <div className="flex items-center gap-2 text-sm mt-1">
                      <span className="text-slate-500 dark:text-slate-400">
                        Provider:
                      </span>
                      <span className="text-slate-700 dark:text-slate-300">
                        {s.provider}
                      </span>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Port Information */}
      {ports && (
        <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50">
          <div className="flex items-center gap-2 mb-3">
            <Server className="w-5 h-5 text-slate-400" />
            <h3 className="font-semibold text-slate-900 dark:text-slate-100">
              Port Configuration
            </h3>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <span className="text-sm text-slate-500 dark:text-slate-400">
                Backend Port
              </span>
              <p className="font-mono text-lg text-slate-700 dark:text-slate-300">
                {ports.backend_port}
              </p>
            </div>
            <div>
              <span className="text-sm text-slate-500 dark:text-slate-400">
                Frontend Port
              </span>
              <p className="font-mono text-lg text-slate-700 dark:text-slate-300">
                {ports.frontend_port}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Configuration Tab Component
function ConfigTab({
  configType,
  title,
  description,
  onUpdate,
  showDimensions = false,
  showVoice = false,
  isSearchConfig = false,
}: {
  configType: ConfigType;
  title: string;
  description: string;
  onUpdate: () => void;
  showDimensions?: boolean;
  showVoice?: boolean;
  isSearchConfig?: boolean;
}) {
  const [configs, setConfigs] = useState<ConfigItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingConfig, setEditingConfig] = useState<ConfigItem | null>(null);
  const [testing, setTesting] = useState<string | null>(null);
  const [testResult, setTestResult] = useState<{
    success: boolean;
    message: string;
  } | null>(null);

  useEffect(() => {
    loadConfigs();
  }, [configType]);

  const loadConfigs = async () => {
    try {
      const res = await fetch(apiUrl(`/api/v1/config/${configType}`));
      if (res.ok) {
        const data = await res.json();
        setConfigs(data.configs || []);
      }
    } catch (e) {
      console.error(`Failed to load ${configType} configs:`, e);
    } finally {
      setLoading(false);
    }
  };

  const setActive = async (configId: string) => {
    try {
      const res = await fetch(
        apiUrl(`/api/v1/config/${configType}/${configId}/active`),
        {
          method: "POST",
        },
      );
      if (res.ok) {
        loadConfigs();
        onUpdate();
      }
    } catch (e) {
      console.error("Failed to set active config:", e);
    }
  };

  const deleteConfig = async (configId: string) => {
    if (!confirm("Are you sure you want to delete this configuration?")) return;

    try {
      const res = await fetch(
        apiUrl(`/api/v1/config/${configType}/${configId}`),
        {
          method: "DELETE",
        },
      );
      if (res.ok) {
        loadConfigs();
        onUpdate();
      }
    } catch (e) {
      console.error("Failed to delete config:", e);
    }
  };

  const testConnection = async (config: ConfigItem) => {
    // Search configs don't support testing
    if (isSearchConfig) return;

    setTesting(config.id);
    setTestResult(null);

    try {
      // Use the config ID based test endpoint - this resolves use_env references on the backend
      const res = await fetch(
        apiUrl(`/api/v1/config/${configType}/${config.id}/test`),
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
        },
      );
      const data = await res.json();
      setTestResult(data);
    } catch (e) {
      setTestResult({ success: false, message: "Connection test failed" });
    } finally {
      setTesting(null);
    }
  };

  if (loading) {
    return (
      <div className="p-8 flex justify-center">
        <Loader2 className="w-6 h-6 animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
            {title}
          </h2>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            {description}
          </p>
        </div>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors"
        >
          <Plus className="w-4 h-4" />
          Add Configuration
        </button>
      </div>

      {/* Add/Edit Form */}
      {(showAddForm || editingConfig) && (
        <ConfigForm
          configType={configType}
          showDimensions={showDimensions}
          showVoice={showVoice}
          isSearchConfig={isSearchConfig}
          editConfig={editingConfig}
          onSuccess={() => {
            setShowAddForm(false);
            setEditingConfig(null);
            loadConfigs();
            onUpdate();
          }}
          onCancel={() => {
            setShowAddForm(false);
            setEditingConfig(null);
          }}
        />
      )}

      {/* Test Result */}
      {testResult && (
        <div
          className={`mb-4 p-3 rounded-lg text-sm ${
            testResult.success
              ? "bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300 border border-green-200 dark:border-green-800"
              : "bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 border border-red-200 dark:border-red-800"
          }`}
        >
          {testResult.message}
        </div>
      )}

      {/* Configuration List */}
      <div className="space-y-3">
        {configs.map((config) => (
          <div
            key={config.id}
            className={`p-4 rounded-xl border transition-all ${
              config.is_active
                ? "border-blue-300 dark:border-blue-700 bg-blue-50 dark:bg-blue-900/20"
                : "border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50"
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {config.is_active && (
                  <div className="w-2 h-2 rounded-full bg-blue-500" />
                )}
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-slate-900 dark:text-slate-100">
                      {config.name}
                    </span>
                    {config.is_default && (
                      <span className="px-2 py-0.5 text-xs bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-400 rounded">
                        Default
                      </span>
                    )}
                    {config.is_active && (
                      <span className="px-2 py-0.5 text-xs bg-blue-100 dark:bg-blue-800 text-blue-700 dark:text-blue-300 rounded">
                        Active
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-3 mt-1 text-sm text-slate-500 dark:text-slate-400">
                    <span>Provider: {config.provider}</span>
                    {config.model && <span>Model: {config.model}</span>}
                    {showDimensions && config.dimensions && (
                      <span>Dimensions: {config.dimensions}</span>
                    )}
                    {showVoice && config.voice && (
                      <span>Voice: {config.voice}</span>
                    )}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                {!config.is_active && (
                  <button
                    onClick={() => setActive(config.id)}
                    className="px-3 py-1.5 text-sm text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded-lg transition-colors"
                  >
                    Set Active
                  </button>
                )}
                {!isSearchConfig && (
                  <button
                    onClick={() => testConnection(config)}
                    disabled={testing === config.id}
                    className="px-3 py-1.5 text-sm text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
                  >
                    {testing === config.id ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      "Test"
                    )}
                  </button>
                )}
                {!config.is_default && (
                  <button
                    onClick={() => {
                      setEditingConfig(config);
                      setShowAddForm(false);
                    }}
                    className="p-1.5 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
                    title="Edit"
                  >
                    <Pencil className="w-4 h-4" />
                  </button>
                )}
                {!config.is_default && (
                  <button
                    onClick={() => deleteConfig(config.id)}
                    className="p-1.5 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/30 rounded-lg transition-colors"
                    title="Delete"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}

        {configs.length === 0 && (
          <div className="text-center py-8 text-slate-500 dark:text-slate-400">
            No configurations found. Add one to get started.
          </div>
        )}
      </div>
    </div>
  );
}

// Configuration Form Component (Add/Edit)
function ConfigForm({
  configType,
  showDimensions,
  showVoice,
  isSearchConfig,
  editConfig,
  onSuccess,
  onCancel,
}: {
  configType: ConfigType;
  showDimensions: boolean;
  showVoice: boolean;
  isSearchConfig: boolean;
  editConfig?: ConfigItem | null;
  onSuccess: () => void;
  onCancel: () => void;
}) {
  const isEditMode = !!editConfig;
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [testResult, setTestResult] = useState<{
    success: boolean;
    message: string;
  } | null>(null);

  // Helper to check if a value uses env reference format {use_env: "VAR_NAME"}
  const isEnvReference = (value: any): boolean => {
    return !!(value && typeof value === "object" && "use_env" in value);
  };

  // Helper to get display value - returns empty string if env reference, otherwise the value
  const getDisplayValue = (value: any): string => {
    if (isEnvReference(value)) return "";
    return typeof value === "string" ? value : "";
  };

  // Check initial env reference states (computed once based on editConfig)
  const initialUseEnvBaseUrl = editConfig
    ? isEnvReference(editConfig.base_url)
    : false;
  const initialUseEnvApiKey = editConfig
    ? isEnvReference(editConfig.api_key)
    : false;

  // Form state - initialize from editConfig if editing, handle env references
  const [name, setName] = useState(editConfig?.name || "");
  const [provider, setProvider] = useState(
    editConfig?.provider || PROVIDER_OPTIONS[configType][0],
  );
  const [baseUrl, setBaseUrl] = useState(
    editConfig ? getDisplayValue(editConfig.base_url) : "",
  );
  const [useEnvBaseUrl, setUseEnvBaseUrl] =
    useState<boolean>(initialUseEnvBaseUrl);
  const [apiKey, setApiKey] = useState(""); // Never pre-fill API key for security
  const [useEnvApiKey, setUseEnvApiKey] =
    useState<boolean>(initialUseEnvApiKey);
  const [showApiKey, setShowApiKey] = useState(false);
  const [model, setModel] = useState(editConfig?.model || "");
  const [dimensions, setDimensions] = useState(editConfig?.dimensions || 3072);
  const [voice, setVoice] = useState(editConfig?.voice || "alloy");

  // Check if current provider is local (doesn't require API key)
  const isLocalProvider = LOCAL_PROVIDERS.includes(provider);

  // Auto-fill base URL when switching to local provider
  const handleProviderChange = (newProvider: string) => {
    setProvider(newProvider);
    if (
      LOCAL_PROVIDERS.includes(newProvider) &&
      LOCAL_PROVIDER_URLS[newProvider]
    ) {
      setBaseUrl(LOCAL_PROVIDER_URLS[newProvider]);
      setUseEnvBaseUrl(false);
      setUseEnvApiKey(false);
      setApiKey("");
    }
  };

  // Test connection before saving
  const handleTestConnection = async () => {
    if (isSearchConfig) return;

    // Validate required fields
    if (!useEnvBaseUrl && !baseUrl) {
      setTestResult({
        success: false,
        message: "Base URL is required for testing",
      });
      return;
    }
    if (!isLocalProvider && !useEnvApiKey && !apiKey) {
      setTestResult({
        success: false,
        message: "API Key is required for cloud providers",
      });
      return;
    }
    if (!model) {
      setTestResult({ success: false, message: "Model name is required" });
      return;
    }
    if (configType === "embedding" && !dimensions) {
      setTestResult({
        success: false,
        message: "Dimensions is required for embedding models",
      });
      return;
    }

    setTesting(true);
    setTestResult(null);

    try {
      const res = await fetch(apiUrl(`/api/v1/config/${configType}/test`), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          provider,
          // Send use_env object if using env, otherwise send the actual value
          base_url: useEnvBaseUrl
            ? { use_env: getEnvVarForBaseUrl(configType) }
            : baseUrl,
          api_key: isLocalProvider
            ? ""
            : useEnvApiKey
              ? { use_env: getEnvVarForApiKey(configType) }
              : apiKey,
          model,
          // Include dimensions for embedding configs
          ...(configType === "embedding"
            ? { dimensions: Number(dimensions) }
            : {}),
          // Include voice for TTS configs
          ...(configType === "tts" && voice ? { voice } : {}),
        }),
      });
      const data = await res.json();
      // Ensure message is not empty
      setTestResult({
        success: data.success ?? false,
        message:
          data.message ||
          (data.success ? "Connection successful" : "Connection failed"),
      });
    } catch (e: any) {
      setTestResult({
        success: false,
        message: e?.message || "Connection test failed - network error",
      });
    } finally {
      setTesting(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError(null);

    try {
      const payload: Record<string, any> = {
        name,
        provider,
        // For local providers, API key is optional; for cloud providers, use env or direct value
        api_key: isLocalProvider
          ? apiKey || "" // Empty string for local providers if not provided
          : useEnvApiKey
            ? { use_env: getEnvVarForApiKey(configType) }
            : apiKey,
      };

      if (!isSearchConfig) {
        payload.base_url = useEnvBaseUrl
          ? { use_env: getEnvVarForBaseUrl(configType) }
          : baseUrl;
        payload.model = model;
      }

      if (showDimensions) {
        payload.dimensions = dimensions;
      }

      if (showVoice) {
        payload.voice = voice;
      }

      // Use PUT for edit, POST for add
      const url = isEditMode
        ? apiUrl(`/api/v1/config/${configType}/${editConfig.id}`)
        : apiUrl(`/api/v1/config/${configType}`);
      const method = isEditMode ? "PUT" : "POST";

      const res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        onSuccess();
      } else {
        const data = await res.json();
        setError(
          data.detail ||
            `Failed to ${isEditMode ? "update" : "add"} configuration`,
        );
      }
    } catch (e) {
      setError(`Failed to ${isEditMode ? "update" : "add"} configuration`);
    } finally {
      setSaving(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="mb-6 p-4 rounded-xl border border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-900/20"
    >
      <h3 className="font-medium text-slate-900 dark:text-slate-100 mb-4">
        {isEditMode
          ? `Edit Configuration: ${editConfig.name}`
          : "Add New Configuration"}
      </h3>

      {error && (
        <div className="mb-4 p-3 rounded-lg bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 text-sm border border-red-200 dark:border-red-800">
          {error}
        </div>
      )}

      {testResult && (
        <div
          className={`mb-4 p-3 rounded-lg text-sm ${
            testResult.success
              ? "bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300 border border-green-200 dark:border-green-800"
              : "bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 border border-red-200 dark:border-red-800"
          }`}
        >
          {testResult.message}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Name */}
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
            Name
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            placeholder="My Configuration"
            className="w-full px-3 py-2 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Provider */}
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
            Provider
          </label>
          <div className="relative">
            <select
              value={provider}
              onChange={(e) => handleProviderChange(e.target.value)}
              className="w-full px-3 py-2 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 rounded-lg text-sm appearance-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {PROVIDER_OPTIONS[configType].map((p) => (
                <option key={p} value={p}>
                  {p}
                  {LOCAL_PROVIDERS.includes(p) ? " (local)" : ""}
                </option>
              ))}
            </select>
            <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
          </div>
        </div>

        {/* Base URL (not for search) */}
        {!isSearchConfig && (
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              Base URL
              {useEnvBaseUrl && (
                <span className="ml-2 text-xs font-normal text-blue-500">
                  (using ${getEnvVarForBaseUrl(configType)})
                </span>
              )}
            </label>
            <div className="flex items-center gap-3">
              <div className="flex-1">
                <input
                  type="text"
                  value={useEnvBaseUrl ? "" : baseUrl}
                  onChange={(e) => setBaseUrl(e.target.value)}
                  disabled={useEnvBaseUrl}
                  placeholder={
                    useEnvBaseUrl
                      ? `Using ${getEnvVarForBaseUrl(configType)} from .env`
                      : "https://api.openai.com/v1"
                  }
                  className={`w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    useEnvBaseUrl
                      ? "bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800 text-blue-600 dark:text-blue-400 italic"
                      : "bg-white dark:bg-slate-800 border-slate-300 dark:border-slate-600"
                  }`}
                />
              </div>
              <label className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400 whitespace-nowrap">
                <input
                  type="checkbox"
                  checked={useEnvBaseUrl}
                  onChange={(e) => {
                    setUseEnvBaseUrl(e.target.checked);
                    if (e.target.checked) setBaseUrl("");
                  }}
                  className="rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                />
                Use .env
              </label>
            </div>
          </div>
        )}

        {/* API Key - Optional for local providers */}
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
            API Key
            {isLocalProvider ? (
              <span className="ml-2 text-xs font-normal text-slate-400">
                (optional for local providers)
              </span>
            ) : useEnvApiKey ? (
              <span className="ml-2 text-xs font-normal text-blue-500">
                (using ${getEnvVarForApiKey(configType)})
              </span>
            ) : null}
          </label>
          <div className="flex items-center gap-3">
            <div className="flex-1 relative">
              <input
                type={showApiKey ? "text" : "password"}
                value={useEnvApiKey ? "" : apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                disabled={useEnvApiKey}
                placeholder={
                  isLocalProvider
                    ? "Not required"
                    : useEnvApiKey
                      ? `Using ${getEnvVarForApiKey(configType)} from .env`
                      : "sk-..."
                }
                className={`w-full px-3 py-2 pr-10 border rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  useEnvApiKey
                    ? "bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800 text-blue-600 dark:text-blue-400 italic"
                    : "bg-white dark:bg-slate-800 border-slate-300 dark:border-slate-600"
                }`}
              />
              {!useEnvApiKey && (
                <button
                  type="button"
                  onClick={() => setShowApiKey(!showApiKey)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                >
                  {showApiKey ? (
                    <EyeOff className="w-4 h-4" />
                  ) : (
                    <Eye className="w-4 h-4" />
                  )}
                </button>
              )}
            </div>
            {!isLocalProvider && (
              <label className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400 whitespace-nowrap">
                <input
                  type="checkbox"
                  checked={useEnvApiKey}
                  onChange={(e) => {
                    setUseEnvApiKey(e.target.checked);
                    if (e.target.checked) setApiKey("");
                  }}
                  className="rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                />
                Use .env
              </label>
            )}
          </div>
        </div>

        {/* Model (not for search) */}
        {!isSearchConfig && (
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              Model
            </label>
            <input
              type="text"
              value={model}
              onChange={(e) => setModel(e.target.value)}
              required
              placeholder="gpt-4o"
              className="w-full px-3 py-2 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        )}

        {/* Dimensions (embedding only) */}
        {showDimensions && (
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              Dimensions
            </label>
            <input
              type="number"
              value={dimensions}
              onChange={(e) => setDimensions(parseInt(e.target.value))}
              className="w-full px-3 py-2 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        )}

        {/* Voice (TTS only) */}
        {showVoice && (
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              Voice
            </label>
            <div className="relative">
              <select
                value={voice}
                onChange={(e) => setVoice(e.target.value)}
                className="w-full px-3 py-2 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 rounded-lg text-sm appearance-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {VOICE_OPTIONS.map((v) => (
                  <option key={v} value={v}>
                    {v}
                  </option>
                ))}
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
            </div>
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="flex justify-between items-center mt-4">
        {/* Test Connection Button (left side) */}
        <div>
          {!isSearchConfig && (
            <button
              type="button"
              onClick={handleTestConnection}
              disabled={testing || (!baseUrl && !useEnvBaseUrl)}
              className="flex items-center gap-2 px-4 py-2 text-sm text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700 disabled:opacity-50 rounded-lg transition-colors"
            >
              {testing ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <TestTube className="w-4 h-4" />
              )}
              Test Connection
            </button>
          )}
        </div>

        {/* Cancel and Save Buttons (right side) */}
        <div className="flex gap-3">
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 text-sm text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={saving}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white rounded-lg text-sm font-medium transition-colors"
          >
            {saving ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : isEditMode ? (
              <Check className="w-4 h-4" />
            ) : (
              <Plus className="w-4 h-4" />
            )}
            {isEditMode ? "Save Changes" : "Add Configuration"}
          </button>
        </div>
      </div>
    </form>
  );
}

// Helper functions to get env var names
function getEnvVarForBaseUrl(configType: ConfigType): string {
  const mapping: Record<ConfigType, string> = {
    llm: "LLM_HOST",
    embedding: "EMBEDDING_HOST",
    tts: "TTS_URL",
    search: "SEARCH_PROVIDER", // Provider name, not URL (search uses SEARCH_API_KEY for auth)
  };
  return mapping[configType];
}

function getEnvVarForApiKey(configType: ConfigType): string {
  const mapping: Record<ConfigType, string> = {
    llm: "LLM_API_KEY",
    embedding: "EMBEDDING_API_KEY",
    tts: "TTS_API_KEY",
    search: "SEARCH_API_KEY", // Unified API key for all search providers
  };
  return mapping[configType];
}
