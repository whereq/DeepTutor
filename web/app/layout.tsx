import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import ThemeScript from "@/components/ThemeScript";
import { AppShellProvider } from "@/context/AppShellContext";
import { I18nClientBridge } from "@/i18n/I18nClientBridge";

const font = Inter({
  subsets: ["latin"],
  display: "swap",
  fallback: ["system-ui", "sans-serif"],
});

export const metadata: Metadata = {
  title: "DeepTutor",
  description: "Agent-native intelligent learning companion",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <ThemeScript />
      </head>
      <body className={`${font.className} bg-[var(--background)] text-[var(--foreground)]`}>
        <AppShellProvider>
          <I18nClientBridge>
            {children}
          </I18nClientBridge>
        </AppShellProvider>
      </body>
    </html>
  );
}
