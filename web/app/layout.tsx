import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/Sidebar";
import ThemeScript from "@/components/ThemeScript";
import { UnifiedChatProvider } from "@/context/UnifiedChatContext";
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
        <UnifiedChatProvider>
          <I18nClientBridge>
            <div className="flex h-screen overflow-hidden">
              <Sidebar />
              <main className="flex-1 overflow-hidden bg-[var(--background)]">{children}</main>
            </div>
          </I18nClientBridge>
        </UnifiedChatProvider>
      </body>
    </html>
  );
}
