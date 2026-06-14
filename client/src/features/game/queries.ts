import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import * as api from '@/features/game/api'

export const gameKeys = {
  all: ['game'] as const,
  profile: () => [...gameKeys.all, 'profile'] as const,
  connections: () => [...gameKeys.all, 'connections'] as const,
  leaderboard: (period: 'all' | 'today') => [...gameKeys.all, 'leaderboard', period] as const,
  transactions: () => [...gameKeys.all, 'transactions'] as const,
}

export const useProfile = (enabled = true) =>
  useQuery({ queryKey: gameKeys.profile(), queryFn: api.getProfile, enabled })

export const useConnections = (enabled: boolean) =>
  useQuery({ queryKey: gameKeys.connections(), queryFn: api.getConnections, enabled })

export const useLeaderboard = (period: 'all' | 'today', enabled: boolean) =>
  useQuery({
    queryKey: gameKeys.leaderboard(period),
    queryFn: () => api.getLeaderboard(period),
    enabled,
  })

export const useTransactions = (enabled: boolean) =>
  useQuery({ queryKey: gameKeys.transactions(), queryFn: api.listTransactions, enabled })

export const useAttemptConnections = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ groups, durationSeconds }: { groups: string[][]; durationSeconds: number }) =>
      api.attemptConnections(groups, durationSeconds),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: gameKeys.profile() })
      void queryClient.invalidateQueries({ queryKey: gameKeys.connections() })
      void queryClient.invalidateQueries({ queryKey: gameKeys.all })
    },
  })
}
