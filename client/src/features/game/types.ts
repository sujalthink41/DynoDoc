/** Mirrors the backend gamification DTOs. */

export interface PlayerProfile {
  coins: number
  lifetime_coins: number
  current_streak: number
  longest_streak: number
  played_today: boolean
}

export interface CoinTxn {
  amount: number
  reason: string
  created_at: string
}

export interface ConnectionsView {
  play_date: string
  tiles: string[]
  group_count: number
  group_size: number
  difficulty: number
  difficulty_label: string
  played: boolean
  solved: boolean
  score: number
}

export interface ConnGroup {
  label: string
  level: number
  members: string[]
}

export interface ConnectionsResult {
  solved: boolean
  correct_groups: number
  total_groups: number
  coins_awarded: number
  current_streak: number
  new_balance: number
  groups: ConnGroup[]
}

export interface LeaderboardEntry {
  rank: number
  name: string
  avatar_url: string | null
  is_me: boolean
  coins: number
  correct: number | null
  duration_seconds: number | null
}

export interface LeaderboardView {
  period: 'all' | 'today'
  top: LeaderboardEntry[]
  me: LeaderboardEntry | null
}
