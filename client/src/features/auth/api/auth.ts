import { apiGet, apiPost } from '@/lib/apiClient'
import { apiUrl } from '@/lib/config'
import type { UserProfile } from '@/features/auth/types'

/** Full-page navigation into the backend's Google OAuth flow. */
export function loginWithGoogle(): void {
  window.location.href = apiUrl('/auth/google/login')
}

export function fetchCurrentUser(): Promise<UserProfile> {
  return apiGet<UserProfile>('/me')
}

export function logout(): Promise<void> {
  return apiPost('/auth/logout')
}
