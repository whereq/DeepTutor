import { apiUrl } from "@/lib/api";
import { invalidateClientCache, withClientCache } from "@/lib/client-cache";

const SKILLS_CACHE_PREFIX = "skills:";

export interface SkillInfo {
  name: string;
  description: string;
}

export interface SkillDetail extends SkillInfo {
  content: string;
}

export interface CreateSkillPayload {
  name: string;
  description: string;
  content: string;
}

export interface UpdateSkillPayload {
  description?: string;
  content?: string;
  rename_to?: string;
}

async function asJson(response: Response) {
  if (!response.ok) {
    let detail = `${response.status} ${response.statusText}`;
    try {
      const body = await response.json();
      if (body?.detail) detail = String(body.detail);
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  return response.json();
}

export async function listSkills(options?: { force?: boolean }): Promise<SkillInfo[]> {
  return withClientCache<SkillInfo[]>(
    `${SKILLS_CACHE_PREFIX}list`,
    async () => {
      const response = await fetch(apiUrl("/api/v1/skills/list"), { cache: "no-store" });
      const data = await asJson(response);
      const items = Array.isArray(data?.skills) ? data.skills : [];
      return items.map((item: { name?: unknown; description?: unknown }) => ({
        name: String(item?.name ?? ""),
        description: String(item?.description ?? ""),
      }));
    },
    { force: options?.force },
  );
}

export async function getSkill(name: string): Promise<SkillDetail> {
  const response = await fetch(apiUrl(`/api/v1/skills/${encodeURIComponent(name)}`), {
    cache: "no-store",
  });
  const data = await asJson(response);
  return {
    name: String(data?.name ?? name),
    description: String(data?.description ?? ""),
    content: String(data?.content ?? ""),
  };
}

export async function createSkill(payload: CreateSkillPayload): Promise<SkillInfo> {
  const response = await fetch(apiUrl("/api/v1/skills/create"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await asJson(response);
  invalidateSkillsCache();
  return {
    name: String(data?.name ?? payload.name),
    description: String(data?.description ?? payload.description ?? ""),
  };
}

export async function updateSkill(
  name: string,
  payload: UpdateSkillPayload,
): Promise<SkillInfo> {
  const response = await fetch(apiUrl(`/api/v1/skills/${encodeURIComponent(name)}`), {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await asJson(response);
  invalidateSkillsCache();
  return {
    name: String(data?.name ?? name),
    description: String(data?.description ?? ""),
  };
}

export async function deleteSkill(name: string): Promise<void> {
  const response = await fetch(apiUrl(`/api/v1/skills/${encodeURIComponent(name)}`), {
    method: "DELETE",
  });
  await asJson(response);
  invalidateSkillsCache();
}

export function invalidateSkillsCache() {
  invalidateClientCache(SKILLS_CACHE_PREFIX);
}
