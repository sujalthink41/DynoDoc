import { useCallback, useEffect, useState } from 'react'

import { fetchCurrentUser } from '@/features/auth/api/auth'
import type { UserProfile } from '@/features/auth/types'

export type AuthState =
  | { status: 'loading' }
  | { status: 'authenticated'; user: UserProfile }
  | { status: 'anonymous' }

/** Resolves the current user from the session cookie (GET /me). */
export function useCurrentUser(): { state: AuthState; reload: () => void } {
  const [state, setState] = useState<AuthState>({ status: 'loading' })

  // Fetches and updates state only in the async callbacks (no synchronous
  // setState in the effect body).
  const load = useCallback(() => {
    fetchCurrentUser()
      .then((user) => setState({ status: 'authenticated', user }))
      .catch(() => setState({ status: 'anonymous' }))
  }, [])

  useEffect(() => {
    load()
  }, [load])

  const reload = useCallback(() => {
    setState({ status: 'loading' })
    load()
  }, [load])

  return { state, reload }
}
