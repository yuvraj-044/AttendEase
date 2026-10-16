import type { DashboardData, EventItem, Role, User } from "./types"

interface SessionResponse {
  user: User
  csrf_token: string
}

export class ApiError extends Error {
  status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = "ApiError"
    this.status = status
  }
}

function csrfToken() {
  return document.cookie
    .split("; ")
    .find((item) => item.startsWith("csrftoken="))
    ?.split("=")
    .slice(1)
    .join("=")
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers)
  if (options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json")
  }
  const token = csrfToken()
  if (token && options.method && options.method !== "GET") {
    headers.set("X-CSRFToken", decodeURIComponent(token))
  }
  const response = await fetch(path, {
    ...options,
    headers,
    credentials: "same-origin",
  })
  if (!response.ok) {
    let message = `Request failed (${response.status}).`
    try {
      const body = await response.json()
      message = body.error || message
    } catch {
      // Keep the HTTP error visible if the server did not return JSON.
    }
    throw new ApiError(message, response.status)
  }
  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}

export const api = {
  session: () => request<SessionResponse>("/api/session/"),
  dashboard: (role: Role, status: string, month: string) => {
    const params = new URLSearchParams()
    if (status && status !== "All" && status !== "All Active") {
      params.set("status", status)
    }
    if (role === "teacher" && month) params.set("month", month)
    const query = params.toString()
    return request<DashboardData>(`/api/dashboard/${query ? `?${query}` : ""}`)
  },
  events: () => request<{ events: EventItem[] }>("/api/events/"),
  createEvent: (payload: Record<string, string | boolean>) =>
    request<{ event: EventItem }>("/api/events/", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  createRequest: (payload: Record<string, string | number>) =>
    request<{ request: unknown }>("/api/requests/", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  reviewRequest: (
    id: number,
    action: "approve" | "reject",
    remarks: string,
  ) =>
    request<{ request: unknown }>(`/api/requests/${id}/review/`, {
      method: "POST",
      body: JSON.stringify({ action, remarks }),
    }),
  markAttendance: (id: number) =>
    request<{ request: unknown }>(`/api/requests/${id}/attendance/`, {
      method: "POST",
      body: JSON.stringify({}),
    }),
}
