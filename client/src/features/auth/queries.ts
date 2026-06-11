import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { fetchCurrentUser, logout } from '@/features/auth/api/auth'
import type { UserProfile } from '@/features/auth/types'

export const ME_QUERY_KEY = ['me'] as const

export type AuthState =
  | { status: 'loading' }
  | { status: 'anonymous' }
  | { status: 'authenticated'; user: UserProfile }

/** The current user (GET /me). 401 → treated as anonymous, not an error to retry. */
function useMe() {
  return useQuery<UserProfile>({
    queryKey: ME_QUERY_KEY,
    queryFn: fetchCurrentUser,
    retry: false,
    staleTime: 60_000,
  })
}

/** Single source of auth state for the whole app. */
export function useAuth(): AuthState {
  const { data, isPending, isError } = useMe()
  if (isPending) return { status: 'loading' }
  if (isError || !data) return { status: 'anonymous' }
  return { status: 'authenticated', user: data }
}

export function useLogout() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: logout,
    onSuccess: () => {
      queryClient.setQueryData(ME_QUERY_KEY, null)
      void queryClient.invalidateQueries({ queryKey: ME_QUERY_KEY })
    },
  })
}
