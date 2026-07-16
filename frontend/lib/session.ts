const SESSION_KEY = "dataspot_session_id";

/**
 * Per-browser identifier used to scope dataset visibility. Reused as the
 * `projectId` on every dataset so visitors never see each other's uploads,
 * without needing a real auth system.
 */
export function getSessionId(): string {
  if (typeof window === "undefined") return "server";

  let id = localStorage.getItem(SESSION_KEY);
  if (!id) {
    id = `sess_${crypto.randomUUID()}`;
    localStorage.setItem(SESSION_KEY, id);
  }
  return id;
}
