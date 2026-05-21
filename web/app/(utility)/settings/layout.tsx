import SettingsMiniNav from "@/components/settings/SettingsMiniNav";
import { SettingsLoadStatusBanner } from "@/components/settings/SettingsLoadStatusBanner";
import { SettingsProvider } from "@/components/settings/SettingsContext";
import { SettingsToolbar } from "@/components/settings/SettingsToolbar";
import { SettingsTourOverlay } from "@/components/settings/SettingsTourOverlay";

export default function SettingsLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <SettingsProvider>
      <div className="flex h-full overflow-hidden">
        <SettingsMiniNav />
        <main className="flex min-w-0 flex-1 flex-col overflow-hidden bg-[var(--background)]">
          <div className="mx-auto w-full max-w-5xl px-10 pt-6">
            <SettingsToolbar />
            <SettingsLoadStatusBanner />
          </div>
          {/* Inner scroll container. Sticky elements inside (e.g. the
              profile-list aside in ServiceConfigEditor) anchor to this
              ancestor instead of <main>, so the left column stays put
              while the right side scrolls. ``min-h-0`` is required for
              the flex child to constrain to remaining space — without
              it, ``overflow-y-auto`` would never clip and sticky would
              keep failing to engage. */}
          <div className="min-h-0 flex-1 overflow-y-auto overflow-x-hidden [scrollbar-gutter:stable]">
            <div className="mx-auto w-full max-w-5xl px-10 pb-16">
              <div className="mt-4">{children}</div>
            </div>
          </div>
        </main>
        <SettingsTourOverlay />
      </div>
    </SettingsProvider>
  );
}
