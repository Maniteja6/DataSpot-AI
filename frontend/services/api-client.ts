const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
export const USE_MOCKS = process.env.NEXT_PUBLIC_USE_MOCKS?.toLowerCase() === "true";

export class ApiClientError extends Error {
  status: number;
  detail?: string;

  constructor(status: number, message: string, detail?: string) {
    super(message);
    this.status = status;
    this.detail = detail;
  }
}

interface RequestOptions extends RequestInit {
  timeoutMs?: number;
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { timeoutMs = 20000, ...init } = options;
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);

  const isFormData = init.body instanceof FormData;

  try {
    const res = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      signal: controller.signal,
      headers: {
        ...(isFormData ? {} : { "Content-Type": "application/json" }),
        ...(init.headers ?? {}),
      },
    });

    if (!res.ok) {
      const body = await res.text().catch(() => undefined);
      throw new ApiClientError(res.status, res.statusText, body);
    }

    return (await res.json()) as T;
  } finally {
    clearTimeout(timeout);
  }
}

export const apiClient = {
  get: <T>(path: string, options?: RequestOptions) =>
    request<T>(path, { ...options, method: "GET" }),
  post: <T>(path: string, body?: unknown, options?: RequestOptions) =>
    request<T>(path, {
      ...options,
      method: "POST",
      body: body instanceof FormData ? body : body ? JSON.stringify(body) : undefined,
    }),
  put: <T>(path: string, body?: unknown, options?: RequestOptions) =>
    request<T>(path, {
      ...options,
      method: "PUT",
      body: body instanceof FormData ? body : body ? JSON.stringify(body) : undefined,
    }),
  delete: <T>(path: string, options?: RequestOptions) =>
    request<T>(path, { ...options, method: "DELETE" }),
};

/**
 * Wraps a real API call with a mock fallback. This keeps every service function
 * calling the real FastAPI/AgentCore backend by default, while allowing the UI
 * to run standalone (NEXT_PUBLIC_USE_MOCKS=true) before the backend is wired up,
 * or to gracefully degrade if a call fails during a demo.
 */
export async function withMockFallback<T>(
  liveCall: () => Promise<T>,
  mockFactory: () => T | Promise<T>
): Promise<T> {
  if (USE_MOCKS) return mockFactory();
  try {
    return await liveCall();
  } catch (err) {
    console.warn("[DataSpot] Live API call failed, falling back to mock data.", err);
    return mockFactory();
  }
}
