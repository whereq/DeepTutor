"use client";

import { useState } from "react";
import { I18nProvider } from "./I18nProvider";

const LANGUAGE_KEY = "deeptutor-language";

export function I18nClientBridge({ children }: { children: React.ReactNode }) {
  const [language] = useState<"en" | "zh">(() => {
    if (typeof window === "undefined") return "en";
    try {
      const stored = window.localStorage.getItem(LANGUAGE_KEY);
      return stored === "zh" || stored === "en" ? stored : "en";
    } catch {
      return "en";
    }
  });

  return <I18nProvider language={language}>{children}</I18nProvider>;
}
