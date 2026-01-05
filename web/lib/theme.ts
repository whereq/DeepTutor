/**
 * Theme persistence utilities
 * Handles light/dark theme with localStorage fallback and system preference detection
 */

export type Theme = "light" | "dark";

const THEME_STORAGE_KEY = "deeptutor-theme";

/**
 * Get the stored theme from localStorage
 */
export function getStoredTheme(): Theme | null {
  if (typeof window === "undefined") return null;
  
  try {
    const stored = localStorage.getItem(THEME_STORAGE_KEY);
    if (stored === "light" || stored === "dark") {
      return stored;
    }
  } catch (e) {
    console.error("Failed to read theme from localStorage", e);
  }
  
  return null;
}

/**
 * Save theme to localStorage
 */
export function saveThemeToStorage(theme: Theme): void {
  if (typeof window === "undefined") return;
  
  try {
    localStorage.setItem(THEME_STORAGE_KEY, theme);
    console.log("[theme.ts] Saved theme to localStorage:", theme);
  } catch (e) {
    console.error("Failed to save theme to localStorage", e);
  }
}

/**
 * Get system preference for theme
 */
export function getSystemTheme(): Theme {
  if (typeof window === "undefined") return "light";
  
  return window.matchMedia("(prefers-color-scheme: dark)").matches
    ? "dark"
    : "light";
}

/**
 * Apply theme to document
 */
export function applyThemeToDocument(theme: Theme): void {
  if (typeof document === "undefined") return;
  
  const html = document.documentElement;
  if (theme === "dark") {
    html.classList.add("dark");
    console.log("[theme.ts] Applied dark theme to document");
  } else {
    html.classList.remove("dark");
    console.log("[theme.ts] Applied light theme to document");
  }
}

/**
 * Initialize theme on app startup
 * Priority: localStorage > system preference > default (light)
 */
export function initializeTheme(): Theme {
  // Check localStorage first
  const stored = getStoredTheme();
  if (stored) {
    applyThemeToDocument(stored);
    return stored;
  }
  
  // Fall back to system preference
  const systemTheme = getSystemTheme();
  applyThemeToDocument(systemTheme);
  return systemTheme;
}

/**
 * Set theme and persist it
 */
export function setTheme(theme: Theme): void {
  console.log("[theme.ts] setTheme called with:", theme);
  applyThemeToDocument(theme);
  saveThemeToStorage(theme);
}
