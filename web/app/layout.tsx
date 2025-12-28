import type { Metadata } from "next";
import { Plus_Jakarta_Sans } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/Sidebar";
import { GlobalProvider } from "@/context/GlobalContext";

// Use more modern, geometric fonts
const font = Plus_Jakarta_Sans({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "OpenTutor Platform",
  description: "Multi-Agent Teaching & Research Copilot",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={font.className}>
        <GlobalProvider>
          <div className="flex h-screen bg-slate-50 dark:bg-slate-900 overflow-hidden transition-colors duration-200">
            <Sidebar />
            <main className="flex-1 overflow-y-auto bg-slate-50 dark:bg-slate-900">
              <div className="w-full p-8">{children}</div>
            </main>
          </div>
        </GlobalProvider>
      </body>
    </html>
  );
}
