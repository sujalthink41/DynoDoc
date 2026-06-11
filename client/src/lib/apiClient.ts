import { apiUrl } from '@/lib/config'

export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message?: string) {
    super(message ?? `Request failed with status ${status}`)
    this.name = 'ApiError'
    this.status = status
  }
}

async function parse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    throw new ApiError(response.status)
  }
  if (response.status === 204) {
    return undefined as T
  }
  const text = await response.text()
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
