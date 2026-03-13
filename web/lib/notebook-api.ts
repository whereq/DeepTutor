import { apiUrl } from "@/lib/api";
import { invalidateClientCache, withClientCache } from "@/lib/client-cache";

const NOTEBOOK_CACHE_PREFIX = "notebook:";

export interface NotebookSummary {
  id: string;
  name: string;
  description?: string;
  record_count?: number;
  color?: string;
  icon?: string;
  updated_at?: number;
}

export interface NotebookRecordSummary {
  id: string;
  type: string;
  title: string;
  summary?: string;
  user_query?: string;
  output: string;
  metadata?: Record<string, unknown>;
  created_at?: number;
}

export interface NotebookDetail extends NotebookSummary {
  records: NotebookRecordSummary[];
}

export async function listNotebooks(options?: { force?: boolean }) {
  return withClientCache<NotebookSummary[]>(
    `${NOTEBOOK_CACHE_PREFIX}list`,
    async () => {
      const response = await fetch(apiUrl("/api/v1/notebook/list"), {
        cache: "no-store",
      });
      const data = await response.json();
      return Array.isArray(data?.notebooks) ? data.notebooks : [];
    },
    {
      force: options?.force,
    },
  );
}

export async function getNotebookDetail(notebookId: string, options?: { force?: boolean }) {
  return withClientCache<NotebookDetail>(
    `${NOTEBOOK_CACHE_PREFIX}detail:${notebookId}`,
    async () => {
      const response = await fetch(apiUrl(`/api/v1/notebook/${notebookId}`), {
        cache: "no-store",
      });
      return response.json() as Promise<NotebookDetail>;
    },
    {
      ttlMs: 15_000,
      force: options?.force,
    },
  );
}

export function invalidateNotebookCaches() {
  invalidateClientCache(NOTEBOOK_CACHE_PREFIX);
}
