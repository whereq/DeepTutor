import { apiUrl } from "@/lib/api";

export interface WrongAnswer {
  id: number;
  session_id: string;
  session_title: string;
  question_id: string;
  question: string;
  user_answer: string;
  correct_answer: string;
  resolved: boolean;
  created_at: number;
  resolved_at: number | null;
}

export interface WrongAnswerListResponse {
  items: WrongAnswer[];
  total: number;
}

async function expectJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export async function listWrongAnswers(
  filter: { resolved?: boolean; limit?: number; offset?: number } = {},
): Promise<WrongAnswerListResponse> {
  const params = new URLSearchParams();
  if (filter.resolved !== undefined) {
    params.set("resolved", String(filter.resolved));
  }
  if (filter.limit !== undefined) {
    params.set("limit", String(filter.limit));
  }
  if (filter.offset !== undefined) {
    params.set("offset", String(filter.offset));
  }
  const query = params.toString();
  const response = await fetch(
    apiUrl(`/api/v1/wrong-answers${query ? `?${query}` : ""}`),
    { cache: "no-store" },
  );
  return expectJson<WrongAnswerListResponse>(response);
}

export async function updateWrongAnswerResolved(
  id: number,
  resolved: boolean,
): Promise<void> {
  const response = await fetch(apiUrl(`/api/v1/wrong-answers/${id}`), {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resolved }),
  });
  await expectJson<{ updated: boolean }>(response);
}

export async function deleteWrongAnswer(id: number): Promise<void> {
  const response = await fetch(apiUrl(`/api/v1/wrong-answers/${id}`), {
    method: "DELETE",
  });
  await expectJson<{ deleted: boolean }>(response);
}
