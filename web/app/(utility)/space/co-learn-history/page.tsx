"use client";

import { Sparkles } from "lucide-react";
import { useTranslation } from "react-i18next";
import ChatHistorySection from "@/components/space/ChatHistorySection";

export default function SpaceCoLearnHistoryPage() {
  const { t } = useTranslation();
  return (
    <ChatHistorySection
      kind="co_learn"
      icon={Sparkles}
      title={t("Co-Learn History")}
      description={t(
        "Past auto-routed Co-Learn sessions. Reopen any to continue where the agent left off.",
      )}
    />
  );
}
