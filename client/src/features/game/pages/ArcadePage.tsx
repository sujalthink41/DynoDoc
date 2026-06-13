import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'

import { Breadcrumb, HomeIcon } from '@/components/ui/Breadcrumb'
import { DynoCoin } from '@/components/ui/DynoCoin'
import { useConnections, useLeaderboard, useProfile } from '@/features/game/queries'

const MEDALS = ['🥇', '🥈', '🥉']

function StatChip({ icon, value, label }: { icon: ReactNode; value: ReactNode; label: string }) {
  return (
    <div className="flex items-center gap-3 rounded-2xl border border-line bg-elevated/70 px-4 py-3 backdrop-blur-xl">
      <span className="flex h-7 w-7 items-center justify-center text-2xl">{icon}</span>
      <div>
        <p className="font-display text-xl font-bold leading-none text-fg">{value}</p>
        <p className="mt-1 text-xs text-muted">{label}</p>
      </div>
    </div>
  )
}

export function ArcadePage() {
  const { data: player } = useProfile()
  const { data: connections } = useConnections(true)
  const { data: board } = useLeaderboard('all', true)
  const played = connections?.played

  return (
    <main className="relative overflow-hidden">
      {/* Ambient backdrop */}
      <div
        aria-hidden
        className="animate-blob pointer-events-none absolute -left-32 -top-24 h-80 w-80 rounded-full bg-brand/20 blur-3xl"
      />
      <div
        aria-hidden
        className="animate-blob animation-delay-2000 pointer-events-none absolute right-0 top-40 h-80 w-80 rounded-full bg-purple-500/20 blur-3xl"
      />
      <div aria-hidden className="pointer-events-none absolute inset-0 text-muted/40 [mask-image:linear-gradient(to_bottom,black,transparent_60%)] bg-dots" />

      <div className="relative px-6 py-10 sm:px-10">
        <Breadcrumb
          items={[{ label: 'Home', to: '/app', icon: <HomeIcon /> }, { label: 'Games' }]}
        />

        {/* Hero */}
        <div className="mt-6 flex flex-wrap items-end justify-between gap-6">
          <div>
            <span className="inline-flex items-center gap-1.5 rounded-full border border-brand/30 bg-brand/10 px-3 py-1 text-xs font-semibold text-brand">
              🎮 DynoArcade
            </span>
            <h1 className="mt-3 font-display text-4xl font-bold tracking-tight text-fg sm:text-5xl">
              Play. Earn. <span className="bg-gradient-to-r from-brand to-brand-2 bg-clip-text text-transparent">Climb.</span>
            </h1>
            <p className="mt-3 max-w-md text-muted">
              One quick puzzle a day. Build your streak, stack DynoCoins, and rise up the
              leaderboard.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <StatChip icon="🔥" value={player?.current_streak ?? 0} label="day streak" />
            <StatChip
              icon={<DynoCoin className="h-7 w-7" />}
              value={player?.coins ?? 0}
              label="coins"
            />
            <StatChip icon="⭐" value={player?.lifetime_coins ?? 0} label="lifetime" />
          </div>
        </div>

        <div className="mt-10 grid gap-6 lg:grid-cols-[1fr_22rem]">
          {/* Featured game */}
          <section>
            <h2 className="text-xs font-semibold uppercase tracking-wider text-muted">
              Today's games
            </h2>
            <Link to="/games/connections" className="mt-3 block">
              <div className="card-sheen group relative rounded-3xl border border-line bg-gradient-to-br from-purple-500/15 via-brand/10 to-brand-2/15 p-7 shadow-xl transition hover:-translate-y-1 hover:border-brand/40">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-center gap-4">
                    <span className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-purple-500 to-brand text-3xl shadow-lg">
                      🧩
                    </span>
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="font-display text-2xl font-bold text-fg">Connections</h3>
                        {connections && (
                          <span className="rounded-full bg-brand/15 px-2 py-0.5 text-[0.65rem] font-bold uppercase tracking-wide text-brand">
                            {connections.difficulty_label}
                          </span>
                        )}
                      </div>
                      <p className="mt-1 max-w-sm text-sm text-muted">
                        Untangle 16 tech tiles into 4 hidden groups. New puzzle every day.
                      </p>
                    </div>
                  </div>
                </div>
                <div className="mt-6 flex items-center justify-between">
                  <span className="flex items-center gap-1 text-sm text-muted">
                    {played ? (
                      `✅ Solved ${connections?.score}/4 today`
                    ) : (
                      <>
                        Up to 65 <DynoCoin className="h-4 w-4" /> + streak
                      </>
                    )}
                  </span>
                  <span
                    className={`rounded-full px-6 py-2.5 text-sm font-bold shadow-md transition group-hover:scale-105 ${
                      played
                        ? 'bg-surface text-muted'
                        : 'bg-gradient-to-r from-brand to-brand-2 text-white shadow-brand/30'
                    }`}
                  >
                    {played ? 'Review' : 'Play now →'}
                  </span>
                </div>
              </div>
            </Link>

            {/* Coming soon */}
            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              {[
                { icon: '🔤', name: 'TermLE', desc: 'Wordle for tech terms' },
                { icon: '🐛', name: 'Bug Hunt', desc: 'Spot the bug, fast' },
              ].map((g) => (
                <div
                  key={g.name}
                  className="flex items-center gap-3 rounded-2xl border border-dashed border-line bg-elevated/40 p-4 opacity-70"
                >
                  <span className="text-2xl grayscale">{g.icon}</span>
                  <div>
                    <p className="text-sm font-semibold text-fg">{g.name}</p>
                    <p className="text-xs text-muted">{g.desc}</p>
                  </div>
                  <span className="ml-auto rounded-full bg-surface px-2.5 py-1 text-[0.65rem] font-semibold uppercase text-muted">
                    Soon
                  </span>
                </div>
              ))}
            </div>
          </section>

          {/* Leaderboard teaser */}
          <section>
            <div className="flex items-center justify-between">
              <h2 className="text-xs font-semibold uppercase tracking-wider text-muted">
                Top players
              </h2>
              <Link
                to="/games/leaderboard"
                className="text-sm font-medium text-brand hover:underline"
              >
                View all →
              </Link>
            </div>
            <div className="mt-3 rounded-3xl border border-line bg-elevated/70 p-3 backdrop-blur-xl">
              {!board || board.top.length === 0 ? (
                <p className="px-3 py-8 text-center text-sm text-muted">
                  No players yet — be the first to score!
                </p>
              ) : (
                <div className="space-y-1">
                  {board.top.slice(0, 5).map((entry) => (
                    <div
                      key={entry.rank}
                      className={`flex items-center gap-3 rounded-xl px-3 py-2.5 ${
                        entry.is_me ? 'bg-brand/10 ring-1 ring-brand/20' : ''
                      }`}
                    >
                      <span className="w-6 text-center text-sm font-bold text-muted">
                        {MEDALS[entry.rank - 1] ?? entry.rank}
                      </span>
                      {entry.avatar_url ? (
                        <img src={entry.avatar_url} alt="" className="h-7 w-7 rounded-full" />
                      ) : (
                        <span className="flex h-7 w-7 items-center justify-center rounded-full bg-surface text-xs font-semibold text-muted">
                          {entry.name.charAt(0).toUpperCase()}
                        </span>
                      )}
                      <span className="flex-1 truncate text-sm text-fg">{entry.name}</span>
                      <span className="flex items-center gap-1 text-sm font-semibold text-amber-500">
                        <DynoCoin className="h-4 w-4" /> {entry.coins}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </section>
        </div>
      </div>
    </main>
  )
}
