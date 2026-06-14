import { apiGet, apiPost, apiPut } from '@/lib/apiClient'
import type {
  CoinTxn,
  ConnectionsResult,
  ConnectionsView,
  DailyBonus,
  LeaderboardView,
  PersonaView,
  PlayerProfile,
  ProfileStats,
  Redemption,
  RewardsView,
} from '@/features/game/types'

export const getProfile = () => apiGet<PlayerProfile>('/game/profile')
export const listTransactions = () => apiGet<CoinTxn[]>('/game/transactions')
export const listRedemptions = () => apiGet<Redemption[]>('/game/redemptions')
export const getConnections = () => apiGet<ConnectionsView>('/game/connections')
export const attemptConnections = (groups: string[][], durationSeconds: number) =>
  apiPost<ConnectionsResult>('/game/connections/attempt', {
    groups,
    duration_seconds: durationSeconds,
  })
export const getLeaderboard = (period: 'all' | 'today') =>
  apiGet<LeaderboardView>(`/game/leaderboard?period=${period}`)
export const getMyStats = () => apiGet<ProfileStats>('/me/stats')
export const getPersona = () => apiGet<PersonaView>('/me/persona')
export const updatePersona = (answers: Record<string, string>) =>
  apiPut<PersonaView>('/me/persona', { answers })
export const claimVisit = () => apiPost<DailyBonus>('/game/visit')
export const getRewards = () => apiGet<RewardsView>('/game/rewards')
export const redeemReward = (key: string, address: string) =>
  apiPost<PlayerProfile>(`/game/rewards/${key}/redeem`, { address })
export const buyCourseSlot = () => apiPost<PlayerProfile>('/game/course-slot')
