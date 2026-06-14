import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import * as api from '@/features/game/api'

export const gameKeys = {
  all: ['game'] as const,
  profile: () => [...gameKeys.all, 'profile'] as const,
  connections: () => [...gameKeys.all, 'connections'] as const,
  leaderboard: (period: 'all' | 'today') => [...gameKeys.all, 'leaderboard', period] as const,
  transactions: () => [...gameKeys.all, 'transactions'] as const,
  redemptions: () => [...gameKeys.all, 'redemptions'] as const,
  stats: () => [...gameKeys.all, 'stats'] as const,
  persona: () => [...gameKeys.all, 'persona'] as const,
  rewards: () => [...gameKeys.all, 'rewards'] as const,
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

export const useMyStats = (enabled: boolean) =>
  useQuery({ queryKey: gameKeys.stats(), queryFn: api.getMyStats, enabled })

export const useRedemptions = (enabled: boolean) =>
  useQuery({ queryKey: gameKeys.redemptions(), queryFn: api.listRedemptions, enabled })

export const usePersona = (enabled: boolean) =>
  useQuery({ queryKey: gameKeys.persona(), queryFn: api.getPersona, enabled })

export const useUpdatePersona = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: api.updatePersona,
    onSuccess: (data) => queryClient.setQueryData(gameKeys.persona(), data),
  })
}

export const useRewards = (enabled: boolean) =>
  useQuery({ queryKey: gameKeys.rewards(), queryFn: api.getRewards, enabled })

export const useClaimVisit = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: api.claimVisit,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: gameKeys.profile() }),
  })
}

export const useRedeemReward = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ key, address }: { key: string; address: string }) =>
      api.redeemReward(key, address),
    onSuccess: (profile) => {
      // Push the fresh profile straight into the cache so balances update instantly.
      queryClient.setQueryData(gameKeys.profile(), profile)
      void queryClient.invalidateQueries({ queryKey: gameKeys.rewards() })
      void queryClient.invalidateQueries({ queryKey: gameKeys.transactions() })
      void queryClient.invalidateQueries({ queryKey: gameKeys.redemptions() })
    },
  })
}

export const useBuyCourseSlot = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: api.buyCourseSlot,
    onSuccess: (profile) => {
      queryClient.setQueryData(gameKeys.profile(), profile)
      void queryClient.invalidateQueries({ queryKey: gameKeys.transactions() })
    },
  })
}

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
