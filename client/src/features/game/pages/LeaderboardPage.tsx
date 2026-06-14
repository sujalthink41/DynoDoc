import { useState } from 'react'

import { Breadcrumb, HomeIcon } from '@/components/ui/Breadcrumb'
import { Card } from '@/components/ui/Card'
import { DynoCoin } from '@/components/ui/DynoCoin'
import { Spinner } from '@/components/ui/Spinner'
import { useLeaderboard } from '@/features/game/queries'
import type { LeaderboardEntry } from '@/features/game/types'

const MEDALS = ['🥇', '🥈', '🥉']

function mmss(s: number) {
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`
}

function MetricView({ entry, period }: { entry: LeaderboardEntry; period: 'all' | 'today' }) {
  if (period === 'today') {
    return (
      <span className="font-mono">
        {entry.correct ?? 0}/4 · {mmss(entry.duration_seconds ?? 0)}
      </span>
    )
  }
  return (
    <span className="inline-flex items-center gap-1">
      <DynoCoin className="h-3.5 w-3.5" /> {entry.coins}
    </span>
  )
}

function Avatar({ entry, size }: { entry: LeaderboardEntry; size: string }) {
  return entry.avatar_url ? (
    <img src={entry.avatar_url} alt="" className={`${size} rounded-full`} />
  ) : (
    <span
      className={`${size} flex items-center justify-center rounded-full bg-surface font-semibold text-muted`}
    >
      {entry.name.charAt(0).toUpperCase()}
    </span>
  )
}

const PODIUM_TONE = [
  'border-amber-400/50 bg-gradient-to-b from-amber-400/20 to-transparent',
  'border-slate-400/40 bg-gradient-to-b from-slate-400/15 to-transparent',
  'border-orange-500/40 bg-gradient-to-b from-orange-500/15 to-transparent',
]

function Podium({ entries, period }: { entries: LeaderboardEntry[]; period: 'all' | 'today' }) {
  const order = [entries[1], entries[0], entries[2]] // 2nd, 1st, 3rd
  const lift = ['mt-6', 'mt-0', 'mt-10']
  return (
    <div className="mt-6 grid grid-cols-3 items-end gap-3">
      {order.map((entry, i) =>
        entry ? (
          <div key={entry.rank} className={lift[i]}>
            <div
              className={`flex flex-col items-center rounded-2xl border p-4 text-center ${
                PODIUM_TONE[entry.rank - 1]
              } ${entry.is_me ? 'ring-2 ring-brand/40' : ''}`}
            >
              <span className="text-2xl">{MEDALS[entry.rank - 1]}</span>
              <div className="mt-2">
                <Avatar entry={entry} size={entry.rank === 1 ? 'h-14 w-14' : 'h-11 w-11'} />
              </div>
              <p className="mt-2 line-clamp-1 w-full text-sm font-semibold text-fg">{entry.name}</p>
              <p className="mt-0.5 text-xs font-medium text-amber-500">
                <MetricView entry={entry} period={period} />
              </p>
            </div>
          </div>
        ) : (
          <div key={i} />
        ),
      )}
    </div>
  )
}

function Row({ entry, period }: { entry: LeaderboardEntry; period: 'all' | 'today' }) {
  return (
    <div
      className={`flex items-center gap-3 rounded-xl px-3 py-2.5 ${
        entry.is_me ? 'bg-brand/10 ring-1 ring-brand/30' : ''
      }`}
    >
      <span className="w-8 shrink-0 text-center font-display text-sm font-bold text-muted">
        {MEDALS[entry.rank - 1] ?? entry.rank}
      </span>
      {entry.avatar_url ? (
        <img src={entry.avatar_url} alt="" className="h-9 w-9 rounded-full" />
      ) : (
        <span className="flex h-9 w-9 items-center justify-center rounded-full bg-surface text-sm font-semibold text-muted">
          {entry.name.charAt(0).toUpperCase()}
        </span>
      )}
      <span className={`flex-1 truncate text-sm ${entry.is_me ? 'font-semibold text-fg' : 'text-fg'}`}>
        {entry.name}
        {entry.is_me && <span className="ml-1 text-xs text-brand">(you)</span>}
      </span>
      {period === 'today' ? (
        <span className="shrink-0 text-right text-sm">
          <span className="font-semibold text-fg">{entry.correct ?? 0}/4</span>
          <span className="ml-2 font-mono text-xs text-muted">
            ⏱ {mmss(entry.duration_seconds ?? 0)}
          </span>
        </span>
      ) : (
        <span className="flex shrink-0 items-center gap-1 text-sm font-semibold text-amber-500">
          <DynoCoin className="h-4 w-4" /> {entry.coins}
        </span>
      )}
    </div>
  )
}

export function LeaderboardPage() {
  const [period, setPeriod] = useState<'today' | 'all'>('today')
  const { data: board, isPending } = useLeaderboard(period, true)
  const inTop = board?.top.some((e) => e.is_me)

  return (
    <main className="mx-auto max-w-2xl px-6 py-10">
      <Breadcrumb
        items={[
          { label: 'Home', to: '/app', icon: <HomeIcon /> },
          { label: 'Games', to: '/games' },
          { label: 'Leaderboard' },
        ]}
      />

      <h1 className="mt-6 font-display text-3xl font-bold text-fg">🏆 Leaderboard</h1>

      {/* Tabs */}
      <div className="mt-5 inline-flex rounded-full border border-line bg-surface p-1">
        {(['today', 'all'] as const).map((p) => (
          <button
            key={p}
            type="button"
            onClick={() => setPeriod(p)}
            className={`rounded-full px-5 py-2 text-sm font-semibold transition ${
              period === p
                ? 'bg-gradient-to-r from-brand to-brand-2 text-white shadow-sm'
                : 'text-muted hover:text-fg'
            }`}
          >
            {p === 'today' ? "Today's race" : 'All-time'}
          </button>
        ))}
      </div>

      {board && board.top.length >= 3 && <Podium entries={board.top} period={period} />}

      <Card className="mt-5 p-3">
        {isPending || !board ? (
          <div className="flex justify-center py-10">
            <Spinner />
          </div>
        ) : board.top.length === 0 ? (
          <p className="px-3 py-10 text-center text-sm text-muted">
            {period === 'today'
              ? 'No one has played today yet — be the first on the board!'
              : 'No players yet — earn coins to claim the top spot!'}
          </p>
        ) : (
          <div className="space-y-1">
            {board.top.map((entry) => (
              <Row key={entry.rank} entry={entry} period={period} />
            ))}
            {!inTop && board.me && (
              <>
                <div className="py-1 text-center text-xs text-muted">···</div>
                <Row entry={board.me} period={period} />
              </>
            )}
          </div>
        )}
      </Card>

      <p className="mt-3 text-center text-xs text-muted">
        {period === 'today'
          ? 'Ranked by groups solved, then fastest time.'
          : 'Ranked by all-time DynoCoins earned.'}
      </p>
    </main>
  )
}
