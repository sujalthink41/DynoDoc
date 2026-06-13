import { apiGet, apiPost } from '@/lib/apiClient'
import type {
  CoinTxn,
  ConnectionsResult,
  ConnectionsView,
  LeaderboardView,
  PlayerProfile,
} from '@/features/game/types'

export const getProfile = () => apiGet<PlayerProfile>('/game/profile')
export const listTransactions = () => apiGet<CoinTxn[]>('/game/transactions')
export const getConnections = () => apiGet<ConnectionsView>('/game/connections')
export const attemptConnections = (groups: string[][], durationSeconds: number) =>
  apiPost<ConnectionsResult>('/game/connections/attempt', {
    groups,
    duration_seconds: durationSeconds,
  })
export const getLeaderboard = (period: 'all' | 'today') =>
  apiGet<LeaderboardView>(`/game/leaderboard?period=${period}`)
