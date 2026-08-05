const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
}

export interface Session {
  session_id: string
  created_at: string
  messages?: ChatMessage[]
}

export interface ToolDefinition {
  name: string
  description: string
  inputSchema: Record<string, unknown>
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    throw new Error(body.detail ?? `Request failed (${response.status})`)
  }
  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}

export const api = {
  health: () => request<{ status: string }>('/health'),
  createSession: () => request<Session>('/api/chat/sessions', { method: 'POST' }),
  getSession: (id: string) => request<Session>(`/api/chat/sessions/${id}`),
  deleteSession: (id: string) => request<void>(`/api/chat/sessions/${id}`, { method: 'DELETE' }),
  sendMessage: (id: string, content: string) => request<{ session_id: string; response: string }>(`/api/chat/sessions/${id}/messages`, {
    method: 'POST', body: JSON.stringify({ content }),
  }),
  tools: () => request<ToolDefinition[]>('/api/mcp/tools'),
}
