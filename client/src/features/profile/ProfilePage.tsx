import type { ReactNode } from 'react'
import { useNavigate } from 'react-router-dom'

import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { DynoCoin } from '@/components/ui/DynoCoin'
import { ProgressBar } from '@/components/ui/ProgressBar'
import { Avatar } from '@/features/auth/components/Avatar'
import { useAuth, useLogout } from '@/features/auth/queries'
import { useMyStats, useRedemptions, useTransactions } from '@/features/game/queries'
import type { Achievement } from '@/features/game/types'
import { PersonaCard } from '@/features/profile/PersonaCard'
import { formatRelative } from '@/lib/relativeTime'

const REASON_LABEL: Record<string, string> = {
  quiz_pass: 'Quiz passed',
  mastery: 'Lesson mastered',
  connections: 'Connections',
  unlock_lesson: 'Unlocked a lesson',
  daily_visit: 'Daily visit',
  daily_rank: '🏆 Daily leaderboard prize',
  lesson_complete: 'Lesson completed',
  course_complete: 'Course completed',
  extra_course: 'Extra course slot',
}

function reasonLabel(reason: string): string {
  if (reason.startsWith('reward:')) return 'Redeemed a reward'
  return REASON_LABEL[reason] ?? reason
}

function StatTile({
  icon,
  value,
  label,
  delay,
}: {
  icon: ReactNode
  value: ReactNode
  label: string
  delay: string
}) {
  return (
    <Card className="flex flex-col items-center gap-1 p-4 text-center transition hover:-translate-y-1 hover:border-brand/40">
      <span className="animate-float flex h-8 items-center justify-center text-2xl" style={{ animationDelay: delay }}>
        {icon}
      </span>
      <p className="font-display text-2xl font-bold text-fg">{value}</p>
      <p className="text-xs text-muted">{label}</p>
    </Card>
  )
}

function Badge({ a }: { a: Achievement }) {
  return (
    <div
      className={`rounded-2xl border p-4 text-center transition ${
        a.unlocked
          ? 'border-brand/40 bg-gradient-to-br from-brand/10 to-brand-2/10 shadow-sm'
          : 'border-line bg-surface/40'
      }`}
    >
      <span
        className={`hover-wiggle inline-block text-4xl ${a.unlocked ? 'animate-float' : 'opacity-30 grayscale'}`}
      >
        {a.icon}
      </span>
      <p className={`mt-2 text-sm font-semibold ${a.unlocked ? 'text-fg' : 'text-muted'}`}>
        {a.title}
      </p>
      <p className="mt-0.5 text-xs text-muted">{a.description}</p>
      {a.unlocked ? (
        <p className="mt-2 text-xs font-bold uppercase tracking-wide text-brand">Unlocked ✓</p>
      ) : (
        <div className="mt-2">
          <ProgressBar value={(a.current / a.goal) * 100} />
          <p className="mt-1 text-[0.7rem] text-muted">
            {a.current}/{a.goal}
          </p>
        </div>
      )}
    </div>
  )
}

export function ProfilePage() {
  const auth = useAuth()
  const logoutMutation = useLogout()
  const navigate = useNavigate()
  const authed = auth.status === 'authenticated'
  const { data: stats } = useMyStats(authed)
  const { data: txns } = useTransactions(authed)
  const { data: redemptions } = useRedemptions(authed)

  if (auth.status !== 'authenticated') return null
  const { user } = auth

  const handleLogout = () => logoutMutation.mutate(undefined, { onSuccess: () => navigate('/') })

  return (
    <main className="mx-auto max-w-5xl">
      {/* Header */}
      <Card className="flex flex-col items-center gap-4 p-6 sm:flex-row sm:text-left">
        <Avatar user={user} className="h-20 w-20 text-2xl" />
        <div className="flex-1 text-center sm:text-left">
          <h1 className="font-display text-2xl font-bold text-fg">
            {user.display_name ?? user.email}
          </h1>
          <p className="text-muted">{user.email}</p>
          {stats && (
            <p className="mt-1 text-sm text-brand">
              🏆 Rank #{stats.rank} · {stats.unlocked_count}/{stats.total_achievements} badges
            </p>
          )}
        </div>
        <Button
          variant="ghost"
          onClick={handleLogout}
          disabled={logoutMutation.isPending}
          className="px-5 py-2.5"
        >
          {logoutMutation.isPending ? 'Logging out…' : 'Log out'}
        </Button>
      </Card>

      {/* Stats */}
      <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
        <StatTile icon="🔥" value={stats?.current_streak ?? 0} label="day streak" delay="0s" />
        <StatTile
          icon={<DynoCoin className="h-7 w-7" />}
          value={stats?.coins ?? 0}
          label="coins"
          delay="0.4s"
        />
        <StatTile icon="⭐" value={stats?.lifetime_coins ?? 0} label="lifetime earned" delay="0.8s" />
        <StatTile icon="📚" value={stats?.lessons_passed ?? 0} label="lessons passed" delay="1.2s" />
        <StatTile icon="💯" value={stats?.lessons_mastered ?? 0} label="mastered" delay="1.6s" />
        <StatTile icon="🧩" value={stats?.connections_solved ?? 0} label="puzzles solved" delay="2s" />
      </div>

      {/* About you (personalization) */}
      <section className="mt-10">
        <PersonaCard />
      </section>

      {/* Achievements */}
      <section className="mt-10">
        <h2 className="font-display text-xl font-semibold text-fg">Achievements</h2>
        {stats ? (
          <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
            {stats.achievements.map((a) => (
              <Badge key={a.key} a={a} />
            ))}
          </div>
        ) : (
          <p className="mt-4 text-sm text-muted">Loading…</p>
        )}
      </section>

      {/* Recent activity */}
      <section className="mt-10">
        <h2 className="font-display text-xl font-semibold text-fg">Recent activity</h2>
        <Card className="mt-4 p-3">
          {!txns || txns.length === 0 ? (
            <p className="px-3 py-6 text-center text-sm text-muted">
              No activity yet — play a game or pass a quiz to earn DynoCoins.
            </p>
          ) : (
            <div className="divide-y divide-line">
              {txns.map((t, i) => (
                <div key={i} className="flex items-center justify-between px-3 py-2.5">
                  <div>
                    <p className="text-sm text-fg">{reasonLabel(t.reason)}</p>
                    <p className="text-xs text-muted">{formatRelative(t.created_at)}</p>
                  </div>
                  <span
                    className={`flex items-center gap-1 text-sm font-semibold ${
                      t.amount >= 0 ? 'text-green-500' : 'text-muted'
                    }`}
                  >
                    {t.amount >= 0 ? '+' : ''}
                    {t.amount} <DynoCoin className="h-3.5 w-3.5" />
                  </span>
                </div>
              ))}
            </div>
          )}
        </Card>
      </section>

      {/* Reward redemptions */}
      <section className="mt-10">
        <h2 className="font-display text-xl font-semibold text-fg">Reward redemptions</h2>
        <Card className="mt-4 p-3">
          {!redemptions || redemptions.length === 0 ? (
            <p className="px-3 py-6 text-center text-sm text-muted">
              No redemptions yet — earn DynoCoins and grab some merch from the Rewards shop.
            </p>
          ) : (
            <div className="divide-y divide-line">
              {redemptions.map((r, i) => (
                <div key={i} className="flex items-center gap-3 px-3 py-3">
                  <span className="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-surface/60 text-2xl">
                    {r.emoji}
                  </span>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center justify-between gap-2">
                      <p className="truncate text-sm font-semibold text-fg">{r.title}</p>
                      <span className="flex shrink-0 items-center gap-1 text-sm font-semibold text-muted">
                        −{r.coins_spent} <DynoCoin className="h-3.5 w-3.5" />
                      </span>
                    </div>
                    <p className="truncate text-xs text-muted" title={r.shipping_address}>
                      🚚 {r.shipping_address}
                    </p>
                    <p className="text-[0.7rem] text-muted">
                      Redeemed {formatRelative(r.created_at)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>
      </section>
    </main>
  )
}
