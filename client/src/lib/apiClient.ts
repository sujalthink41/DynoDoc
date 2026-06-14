import { apiUrl } from '@/lib/config'

export class ApiError extends Error {
  readonly status: number
  /** Machine-readable code from the RFC 9457 problem+json body, if present. */
  readonly code?: string

  constructor(status: number, message?: string, code?: string) {
    super(message ?? `Request failed with status ${status}`)
    this.name = 'ApiError'
    this.status = status
    this.code = code
  }
}

async function parse<T>(response: Response): Promise<T> {
  const text = await response.text()
  if (!response.ok) {
    let code: string | undefined
    let detail: string | undefined
    try {
      const problem = text ? JSON.parse(text) : undefined
      code = problem?.code
      detail = problem?.detail ?? problem?.title
    } catch {
      // non-JSON error body — fall back to the status message
    }
    throw new ApiError(response.status, detail, code)
  }
  if (response.status === 204) {
    return undefined as T
  }
  return (text ? JSON.parse(text) : undefined) as T
}

/** GET JSON. `credentials: 'include'` sends the session cookie. */
export async function apiGet<T>(path: string): Promise<T> {
  return parse<T>(await fetch(apiUrl(path), { credentials: 'include' }))
}

/** POST (optionally with a JSON body). Returns parsed JSON, or undefined for 204. */
export async function apiPost<T = void>(path: string, body?: unknown): Promise<T> {
  return parse<T>(
    await fetch(apiUrl(path), {
      method: 'POST',
      credentials: 'include',
      headers: body !== undefined ? { 'Content-Type': 'application/json' } : undefined,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    }),
  )
}

/** PUT with a JSON body. */
export async function apiPut<T = void>(path: string, body: unknown): Promise<T> {
  return parse<T>(
    await fetch(apiUrl(path), {
      method: 'PUT',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }),
  )
}
