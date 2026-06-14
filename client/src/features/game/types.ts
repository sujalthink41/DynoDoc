/** Mirrors the backend gamification DTOs. */

export interface PlayerProfile {
  coins: number
  lifetime_coins: number
  current_streak: number
  longest_streak: number
  played_today: boolean
  bonus_course_slots: number
}

export interface DailyBonus {
  awarded: number
  coins: number
}

export interface Reward {
  key: string
  title: string
  emoji: string
  cost: number
  claimed: boolean
  affordable: boolean
}

export interface RewardsView {
  coins: number
  rewards: Reward[]
}

export interface CoinTxn {
  amount: number
  reason: string
  created_at: string
}

export interface Redemption {
  item_key: string
  title: string
  emoji: string
  coins_spent: number
  shipping_address: string
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

export interface Achievement {
  key: string
  title: string
  description: string
  icon: string
  goal: number
  current: number
  unlocked: boolean
}

export interface PersonaQuestion {
  key: string
  prompt: string
  emoji: string
  kind: 'choice' | 'text'
  options: string[]
  allow_custom: boolean
  answer: string
}

export interface PersonaView {
  questions: PersonaQuestion[]
  answered: number
  total: number
  percent: number
}

export interface ProfileStats {
  coins: number
  lifetime_coins: number
  current_streak: number
  longest_streak: number
  rank: number
  courses_count: number
  courses_completed: number
  lessons_passed: number
  lessons_mastered: number
  connections_played: number
  connections_solved: number
  unlocked_count: number
  total_achievements: number
  achievements: Achievement[]
}
