import { API_BASE_URL } from '@/lib/config'

export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message?: string) {
    super(message ?? `Request failed with status ${status}`)
    this.name = 'ApiError'
    this.status = status
  }
}

/**
 * GET a JSON resource. `credentials: 'include'` sends the session cookie so the
 * backend can identify the logged-in user.
 */
export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    credentials: 'include',
  })
  if (!response.ok) {
    throw new ApiError(response.status)
  }
  return (await response.json()) as T
}

/** POST with no body (e.g. logout). */
export async function apiPost(path: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    credentials: 'include',
  })
  if (!response.ok) {
    throw new ApiError(response.status)
  }
}
