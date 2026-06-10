import { apiGet, apiPost } from '@/lib/apiClient'
import { API_BASE_URL } from '@/lib/config'
import type { UserProfile } from '@/features/auth/types'

/**
 * Start the Google OAuth flow. This is a full-page navigation (not fetch),
 * because OAuth relies on browser redirects and cookies.
 */
export function loginWithGoogle(): void {
  window.location.href = `${API_BASE_URL}/api/v1/auth/google/login`
}

export function fetchCurrentUser(): Promise<UserProfile> {
  return apiGet<UserProfile>('/api/v1/me')
}

export function logout(): Promise<void> {
  return apiPost('/api/v1/auth/logout')
}
