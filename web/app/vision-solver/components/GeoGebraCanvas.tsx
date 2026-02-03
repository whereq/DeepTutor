"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { Maximize2, Minimize2, RefreshCw } from "lucide-react";
import { useTranslation } from "react-i18next";

interface GGBCommand {
  sequence: number;
  command: string;
  description: string;
}

interface GeoGebraCanvasProps {
  /** GeoGebra commands to execute (parsed format) */
  commands: GGBCommand[];
  /** Unique identifier for this canvas */
  pageId: string;
  /** Title of the canvas */
  title?: string;
  /** Whether the canvas is embedded (compact mode) */
  embedded?: boolean;
  /** Custom height for embedded mode */
  height?: number;
  /** Whether to show the header */
  showHeader?: boolean;
}

// Declare GeoGebra global types
declare global {
  interface Window {
    GGBApplet: any;
  }
}

// Helper function to execute GeoGebra commands
function runGGBCommands(api: any, cmds: GGBCommand[]) {
  if (!api) return;

  try {
    // Sort by sequence and execute
    const sorted = [...cmds].sort((a, b) => a.sequence - b.sequence);

    for (const cmd of sorted) {
      if (cmd.command && cmd.command.trim()) {
        try {
          api.evalCommand(cmd.command);
        } catch (e) {
          console.warn(`GeoGebra command failed: ${cmd.command}`, e);
        }
      }
    }
  } catch (error) {
    console.error("Error executing GeoGebra commands:", error);
  }
}

export function GeoGebraCanvas({
  commands,
  pageId,
  title,
  embedded = false,
  height = 300,
  showHeader = true,
}: GeoGebraCanvasProps) {
  const { t } = useTranslation();
  const containerRef = useRef<HTMLDivElement>(null);
  const ggbContainerRef = useRef<HTMLDivElement | null>(null);
  const appletRef = useRef<any>(null);
  const [isExpanded, setIsExpanded] = useState(false);
  const [isLoaded, setIsLoaded] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const initializedPageRef = useRef<string | null>(null);
  const executedCommandsRef = useRef<Set<string>>(new Set());

  // Load GeoGebra script
  useEffect(() => {
    if (typeof window === "undefined") return;

    // If GGBApplet is already available, defer state update to avoid cascading renders
    if (typeof window.GGBApplet !== "undefined") {
      const timeoutId = setTimeout(() => setIsLoaded(true), 0);
      return () => clearTimeout(timeoutId);
    }

    // Check if script is already being loaded
    const existingScript = document.querySelector(
      'script[src*="geogebra.org/apps/deployggb.js"]',
    );
    if (existingScript) {
      existingScript.addEventListener("load", () => setIsLoaded(true));
      return;
    }

    const script = document.createElement("script");
    script.src = "https://www.geogebra.org/apps/deployggb.js";
    script.async = true;
    script.onload = () => {
      setIsLoaded(true);
    };
    script.onerror = () => {
      console.error("Failed to load GeoGebra script");
      setError("Failed to load GeoGebra library");
      setIsLoading(false);
    };
    document.head.appendChild(script);

    return () => {
      // Don't remove script as it might be used by other instances
    };
  }, []);

  // Cleanup applet function
  const cleanupApplet = useCallback(() => {
    if (appletRef.current) {
      try {
        appletRef.current.remove();
      } catch {
        // Ignore cleanup errors
      }
      appletRef.current = null;
    }
    executedCommandsRef.current.clear();
  }, []);

  // Initialize applet when script is loaded
  useEffect(() => {
    if (!isLoaded || !containerRef.current || typeof window === "undefined")
      return;

    const container = containerRef.current;
    const appletId = `ggb-${pageId}`;

    // If already initialized for this pageId, skip
    if (initializedPageRef.current === pageId && appletRef.current) {
      return;
    }

    // Cleanup previous applet if exists
    if (initializedPageRef.current && initializedPageRef.current !== pageId) {
      cleanupApplet();
    }

    // Use ref to track initialization state to avoid setState in effect body
    initializedPageRef.current = pageId;

    // Create a new div for GeoGebra injection
    const ggbDiv = document.createElement("div");
    ggbDiv.id = `ggb-container-${appletId}`;

    // Clear previous GeoGebra container if exists
    if (
      ggbContainerRef.current &&
      container.contains(ggbContainerRef.current)
    ) {
      container.removeChild(ggbContainerRef.current);
    }

    container.appendChild(ggbDiv);
    ggbContainerRef.current = ggbDiv;

    // Store commands in a variable for the callback
    const cmds = commands;
    const commandsKey = JSON.stringify(cmds);

    const params = {
      id: appletId,
      appName: "classic",
      width: container.offsetWidth || 600,
      height: isExpanded ? 500 : height,
      showToolBar: false,
      showMenuBar: false,
      showAlgebraInput: false,
      showResetIcon: false,
      enableLabelDrags: false,
      enableShiftDragZoom: true,
      enableRightClick: false,
      showFullscreenButton: false,
      showZoomButtons: true,
      capturingThreshold: null,
      showAnimationButton: false,
      preventFocus: true,
      borderColor: "#ffffff",
      appletOnLoad: (api: any) => {
        appletRef.current = api;
        setIsLoading(false);

        // Execute commands only if not already executed
        if (!executedCommandsRef.current.has(commandsKey)) {
          runGGBCommands(api, cmds);
          executedCommandsRef.current.add(commandsKey);
        }
      },
    };

    let errorTimeoutId: NodeJS.Timeout | undefined;
    try {
      const applet = new window.GGBApplet(params, true);
      applet.inject(ggbDiv);
    } catch (err) {
      console.error("Failed to initialize GeoGebra applet:", err);
      // Defer state updates to avoid cascading renders
      errorTimeoutId = setTimeout(() => {
        setError("Failed to initialize GeoGebra");
        setIsLoading(false);
      }, 0);
    }

    return () => {
      // Don't try to remove DOM elements here - let React handle cleanup
      if (errorTimeoutId) clearTimeout(errorTimeoutId);
    };
  }, [isLoaded, pageId, isExpanded, commands, height, cleanupApplet]);

  // Execute new commands when they change
  useEffect(() => {
    if (!commands || commands.length === 0 || !appletRef.current) return;

    const commandsKey = JSON.stringify(commands);

    // Only execute if these commands haven't been executed before
    if (!executedCommandsRef.current.has(commandsKey)) {
      runGGBCommands(appletRef.current, commands);
      executedCommandsRef.current.add(commandsKey);
    }
  }, [commands]);

  // Handle resize
  useEffect(() => {
    if (!containerRef.current || !appletRef.current) return;

    const resizeObserver = new ResizeObserver(() => {
      appletRef.current?.recalculateEnvironments?.();
    });

    resizeObserver.observe(containerRef.current);

    return () => {
      resizeObserver.disconnect();
    };
  }, [isLoaded]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      cleanupApplet();
    };
  }, [cleanupApplet]);

  // Refresh/re-run commands
  const handleRefresh = useCallback(() => {
    if (appletRef.current) {
      try {
        appletRef.current.reset();
        executedCommandsRef.current.clear();
        runGGBCommands(appletRef.current, commands);
        executedCommandsRef.current.add(JSON.stringify(commands));
      } catch {
        // If reset fails, recreate by changing pageId
        initializedPageRef.current = null;
        setIsLoaded(false);
        setTimeout(() => setIsLoaded(true), 100);
      }
    }
  }, [commands]);

  if (commands.length === 0) {
    return null;
  }

  // Container styling based on mode
  const containerClassName = embedded
    ? "flex flex-col bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 overflow-hidden"
    : `bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden transition-all ${
        isExpanded ? "fixed inset-4 z-50" : ""
      }`;

  const canvasHeight = isExpanded ? "calc(100% - 40px)" : `${height}px`;

  return (
    <div className={containerClassName}>
      {/* Header */}
      {showHeader && (
        <div className="flex items-center justify-between px-4 py-2 bg-slate-50 dark:bg-slate-900/50 border-b border-slate-200 dark:border-slate-700">
          <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
            {title || t("GeoGebra Visualization")}
          </span>
          <div className="flex items-center gap-2">
            {isLoading && (
              <span className="text-xs text-slate-500 dark:text-slate-400">
                {t("Loading...")}
              </span>
            )}
            <button
              onClick={handleRefresh}
              className="p-1.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors"
              title={t("Refresh")}
            >
              <RefreshCw className="w-4 h-4" />
            </button>
            {!embedded && (
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="p-1.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors"
                title={isExpanded ? t("Minimize") : t("Maximize")}
              >
                {isExpanded ? (
                  <Minimize2 className="w-4 h-4" />
                ) : (
                  <Maximize2 className="w-4 h-4" />
                )}
              </button>
            )}
          </div>
        </div>
      )}

      {/* Canvas */}
      <div
        ref={containerRef}
        className="relative bg-white flex-1"
        style={{
          minHeight: height,
          height: showHeader ? canvasHeight : "100%",
        }}
      >
        {error ? (
          <div className="absolute inset-0 flex items-center justify-center text-red-500 dark:text-red-400">
            {error}
          </div>
        ) : (
          <>
            {isLoading && (
              <div className="absolute inset-0 flex items-center justify-center bg-slate-50 dark:bg-slate-900/50 z-10">
                <div className="text-center">
                  <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
                  <span className="text-sm text-slate-500 dark:text-slate-400">
                    {t("Loading GeoGebra...")}
                  </span>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Backdrop for expanded mode */}
      {isExpanded && !embedded && (
        <div
          className="fixed inset-0 bg-black/50 -z-10"
          onClick={() => setIsExpanded(false)}
        />
      )}
    </div>
  );
}

export default GeoGebraCanvas;
