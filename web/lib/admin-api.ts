import { apiUrl } from "@/lib/api";

export interface UserRecord {
  username: string;
  role: "admin" | "user";
  created_at: string;
}

export async function listUsers(): Promise<UserRecord[]> {
  const res = await fetch(apiUrl("/api/v1/auth/users"), {
    credentials: "include",
  });
  if (!res.ok) throw new Error("Failed to fetch users");
  return res.json();
}

export async function deleteUser(username: string): Promise<void> {
  const res = await fetch(
    apiUrl(`/api/v1/auth/users/${encodeURIComponent(username)}`),
    {
      method: "DELETE",
      credentials: "include",
    },
  );
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail ?? "Failed to delete user");
  }
}

export async function setUserRole(
  username: string,
  role: "admin" | "user",
): Promise<void> {
  const res = await fetch(
    apiUrl(`/api/v1/auth/users/${encodeURIComponent(username)}/role`),
    {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ role }),
    },
  );
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail ?? "Failed to update role");
  }
}
