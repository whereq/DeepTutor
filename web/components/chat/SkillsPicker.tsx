"use client";

import { useEffect, useMemo, useState } from "react";
import { Check, Loader2, Search, Sparkles, Wand2, X } from "lucide-react";
import { useTranslation } from "react-i18next";
import PickerShell from "@/components/common/PickerShell";
import { listSkills, type SkillInfo } from "@/lib/skills-api";

export interface SkillsPickerSelection {
  auto: boolean;
  skills: string[];
}

interface SkillsPickerProps {
  open: boolean;
  initialAuto: boolean;
  initialSkills: string[];
  onClose: () => void;
  onApply: (selection: SkillsPickerSelection) => void;
}

export default function SkillsPicker({
  open,
  initialAuto,
  initialSkills,
  onClose,
  onApply,
}: SkillsPickerProps) {
  const { t } = useTranslation();
  const [skills, setSkills] = useState<SkillInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [auto, setAuto] = useState(initialAuto);
  const [selected, setSelected] = useState<string[]>(initialSkills);
  const [query, setQuery] = useState("");

  // Sync local state with the parent's current selection every time the
  // picker is reopened so the modal always starts from the latest choice.
  // The IIFE keeps setState calls out of the synchronous effect body to
  // satisfy `react-hooks/set-state-in-effect`.
  useEffect(() => {
    if (!open) return;
    let cancelled = false;
    void (async () => {
      if (cancelled) return;
      setAuto(initialAuto);
      setSelected(initialSkills);
      setQuery("");
    })();
    return () => {
      cancelled = true;
    };
  }, [open, initialAuto, initialSkills]);

  useEffect(() => {
    if (!open) return;
    let mounted = true;
    void (async () => {
      setLoading(true);
      try {
        const items = await listSkills({ force: true });
        if (mounted) setSkills(items);
      } catch {
        if (mounted) setSkills([]);
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => {
      mounted = false;
    };
  }, [open]);

  const filteredSkills = useMemo(() => {
    const keyword = query.trim().toLowerCase();
    if (!keyword) return skills;
    return skills.filter((skill) => {
      const name = skill.name.toLowerCase();
      const desc = (skill.description || "").toLowerCase();
      const tags = (skill.tags || []).join(" ").toLowerCase();
      return (
        name.includes(keyword) ||
        desc.includes(keyword) ||
        tags.includes(keyword)
      );
    });
  }, [skills, query]);

  const toggleSkill = (name: string) => {
    setAuto(false);
    setSelected((prev) =>
      prev.includes(name)
        ? prev.filter((item) => item !== name)
        : [...prev, name],
    );
  };

  const toggleAuto = () => {
    setAuto((prev) => {
      const next = !prev;
      if (next) setSelected([]);
      return next;
    });
  };

  const handleApply = () => {
    onApply({ auto, skills: auto ? [] : selected });
    onClose();
  };

  const handleClear = () => {
    setAuto(false);
    setSelected([]);
  };

  const totalCount = auto ? 1 : selected.length;

  return (
    <PickerShell
      open={open}
      onClose={onClose}
      labelledBy="skills-picker-title"
      className="p-4 backdrop-blur-md"
      backdropClass="bg-[var(--background)]/65"
    >
      <div className="surface-card w-full max-w-3xl overflow-hidden rounded-2xl border border-[var(--border)] bg-[var(--card)] text-[var(--card-foreground)] shadow-[0_22px_70px_rgba(0,0,0,0.18)]">
        <div className="flex items-start justify-between gap-3 border-b border-[var(--border)] px-5 py-4">
          <div className="min-w-0">
            <div className="mb-1 inline-flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-[0.14em] text-[var(--primary)]">
              <Wand2 className="h-3 w-3" />
              {t("Skills Reference")}
            </div>
            <h2
              id="skills-picker-title"
              className="text-lg font-semibold text-[var(--foreground)]"
            >
              {t("Select Skills")}
            </h2>
            <p className="mt-0.5 text-sm text-[var(--muted-foreground)]">
              {t(
                "Pick Auto to let DeepTutor decide, or choose specific skills to apply.",
              )}
            </p>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-2 text-[var(--muted-foreground)] transition-colors hover:bg-[var(--muted)] hover:text-[var(--foreground)]"
            aria-label={t("Close")}
          >
            <X size={18} />
          </button>
        </div>

        <div className="bg-[var(--background)]/40 p-5">
          <button
            type="button"
            onClick={toggleAuto}
            className={`mb-3 flex w-full items-start gap-3 rounded-2xl border px-4 py-3 text-left transition-colors ${
              auto
                ? "border-[var(--primary)]/40 bg-[var(--primary)]/8"
                : "border-[var(--border)] bg-[var(--card)] hover:bg-[var(--muted)]/40"
            }`}
          >
            <div
              className={`mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-md border transition-colors ${
                auto
                  ? "border-[var(--primary)] bg-[var(--primary)] text-[var(--primary-foreground)]"
                  : "border-[var(--border)] text-transparent"
              }`}
            >
              <Check size={12} />
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2 text-[14px] font-medium text-[var(--foreground)]">
                <Sparkles
                  size={14}
                  strokeWidth={1.7}
                  className="text-[var(--primary)]"
                />
                {t("Auto")}
              </div>
              <p className="mt-0.5 text-[12px] leading-5 text-[var(--muted-foreground)]">
                {t("Let the model auto-select relevant skills for this turn.")}
              </p>
            </div>
          </button>

          <div className="mb-4 flex items-center gap-2">
            <div className="relative flex-1">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--muted-foreground)]" />
              <input
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder={t("Search skills by name, description, or tag")}
                className="w-full rounded-xl border border-[var(--border)] bg-[var(--card)] py-2.5 pl-9 pr-3 text-[13px] text-[var(--foreground)] outline-none transition focus:border-[var(--primary)]/50 focus:ring-2 focus:ring-[var(--primary)]/15"
              />
            </div>
            <button
              onClick={handleClear}
              className="rounded-xl border border-[var(--border)] bg-[var(--card)] px-3 py-2.5 text-[12px] font-medium text-[var(--muted-foreground)] transition-colors hover:bg-[var(--muted)] hover:text-[var(--foreground)]"
            >
              {t("Clear")}
            </button>
          </div>

          <div className="max-h-[48vh] overflow-y-auto rounded-2xl border border-[var(--border)] bg-[var(--card)]">
            {loading ? (
              <div className="flex min-h-[220px] items-center justify-center">
                <Loader2 className="h-5 w-5 animate-spin text-[var(--muted-foreground)]" />
              </div>
            ) : filteredSkills.length ? (
              <div className="divide-y divide-[var(--border)]">
                {filteredSkills.map((skill) => {
                  const active = !auto && selected.includes(skill.name);
                  const dimmed = auto;
                  return (
                    <button
                      key={skill.name}
                      onClick={() => toggleSkill(skill.name)}
                      className={`flex w-full items-start gap-3 px-4 py-3 text-left transition-colors ${
                        active
                          ? "bg-[var(--primary)]/8"
                          : "hover:bg-[var(--muted)]/40"
                      } ${dimmed ? "opacity-55" : ""}`}
                    >
                      <div
                        className={`mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-md border transition-colors ${
                          active
                            ? "border-[var(--primary)] bg-[var(--primary)] text-[var(--primary-foreground)]"
                            : "border-[var(--border)] text-transparent"
                        }`}
                      >
                        <Check size={12} />
                      </div>
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2">
                          <span className="truncate text-[14px] font-medium text-[var(--foreground)]">
                            {skill.name}
                          </span>
                          {skill.tags?.length ? (
                            <div className="flex flex-wrap gap-1">
                              {skill.tags.slice(0, 3).map((tag) => (
                                <span
                                  key={tag}
                                  className="rounded-md bg-[var(--muted)] px-1.5 py-0.5 text-[10px] font-medium text-[var(--muted-foreground)]"
                                >
                                  {tag}
                                </span>
                              ))}
                            </div>
                          ) : null}
                        </div>
                        {skill.description ? (
                          <p className="mt-1 line-clamp-2 text-[12px] leading-5 text-[var(--muted-foreground)]">
                            {skill.description}
                          </p>
                        ) : null}
                      </div>
                    </button>
                  );
                })}
              </div>
            ) : (
              <div className="px-6 py-14 text-center text-[13px] text-[var(--muted-foreground)]">
                {skills.length === 0
                  ? t("No skills yet")
                  : t("No matching skills found.")}
              </div>
            )}
          </div>

          <div className="mt-4 flex items-center justify-between gap-3">
            <div className="text-[12px] text-[var(--muted-foreground)]">
              {auto
                ? t("Auto skill selection enabled")
                : selected.length === 1
                  ? t("1 skill selected")
                  : t("{{n}} skills selected", { n: selected.length })}
            </div>
            <button
              onClick={handleApply}
              disabled={totalCount === 0}
              className="btn-primary rounded-xl bg-[var(--primary)] px-4 py-2.5 text-[13px] font-medium text-[var(--primary-foreground)] transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40"
            >
              {auto
                ? t("Use Auto Skills")
                : t("Use Selected Skills ({{n}})", { n: selected.length })}
            </button>
          </div>
        </div>
      </div>
    </PickerShell>
  );
}
