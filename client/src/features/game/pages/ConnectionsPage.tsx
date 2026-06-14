import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { toast } from 'sonner'

import { Breadcrumb, HomeIcon } from '@/components/ui/Breadcrumb'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { DynoCoin } from '@/components/ui/DynoCoin'
import { Spinner } from '@/components/ui/Spinner'
import { useAttemptConnections, useConnections } from '@/features/game/queries'
import type { ConnectionsResult } from '@/features/game/types'
import { celebrate } from '@/lib/celebrate'

const LEVEL_STYLE = [
  'border-amber-400/50 bg-amber-400/15 text-amber-600 dark:text-amber-300',
  'border-green-500/50 bg-green-500/15 text-green-600 dark:text-green-300',
  'border-blue-500/50 bg-blue-500/15 text-blue-600 dark:text-blue-300',
  'border-purple-500/50 bg-purple-500/15 text-purple-600 dark:text-purple-300',
]

export function ConnectionsPage() {
  const { data, isPending } = useConnections(true)
  const attempt = useAttemptConnections()

  const [locked, setLocked] = useState<string[][]>([])
  const [selected, setSelected] = useState<string[]>([])
  const [result, setResult] = useState<ConnectionsResult | null>(null)
  const [elapsed, setElapsed] = useState(0)
  const startRef = useRef<number>(0)

  const playing = Boolean(data && !data.played && !result)
  useEffect(() => {
    if (!playing) return
    if (startRef.current === 0) startRef.current = Date.now()
    const id = setInterval(
      () => setElapsed(Math.floor((Date.now() - startRef.current) / 1000)),
      1000,
    )
    return () => clearInterval(id)
  }, [playing])

  const crumb = (
    <Breadcrumb
      items={[
        { label: 'Home', to: '/app', icon: <HomeIcon /> },
        { label: 'Games', to: '/games' },
        { label: 'Connections' },
      ]}
    />
  )

  if (isPending || !data) {
    return (
      <main className="px-6 py-10">
        {crumb}
        <div className="flex min-h-[50vh] items-center justify-center">
          <Spinner />
        </div>
      </main>
    )
  }

  const groupSize = data.group_size
  const groupCount = data.group_count

  // Already played today (and no fresh result this session).
  if (data.played && !result) {
    return (
      <main className="mx-auto max-w-xl text-center">
        {crumb}
        <Card className="mt-8 p-8">
          <span className="text-5xl">{data.solved ? '🏆' : '🧩'}</span>
          <h1 className="mt-4 font-display text-2xl font-bold text-fg">Done for today!</h1>
          <p className="mt-1 text-muted">
            You found {data.score}/{groupCount} groups. Come back tomorrow for a new puzzle!
          </p>
          <Link to="/games">
            <Button variant="ghost" className="mt-6 px-6 py-3">
              Back to arcade
            </Button>
          </Link>
        </Card>
      </main>
    )
  }

  // Result screen.
  if (result) {
    return (
      <main className="mx-auto max-w-xl text-center">
        {crumb}
        <Card className="mt-8 p-8">
          <span className="text-5xl">{result.solved ? '🎉' : '🧩'}</span>
          <h1 className="mt-3 font-display text-2xl font-bold text-fg">
            {result.solved ? 'Solved it!' : `${result.correct_groups}/${result.total_groups} groups`}
          </h1>
          <div className="mt-5 space-y-2 text-left">
            {result.groups.map((group) => (
              <div
                key={group.label}
                className={`rounded-xl border px-4 py-2.5 ${LEVEL_STYLE[group.level] ?? LEVEL_STYLE[0]}`}
              >
                <p className="text-xs font-bold uppercase tracking-wide">{group.label}</p>
                <p className="mt-0.5 text-sm font-medium">{group.members.join(' · ')}</p>
              </div>
            ))}
          </div>
          <div className="mt-6 flex justify-center gap-4">
            <div className="rounded-2xl bg-amber-400/10 px-5 py-3">
              <p className="flex items-center justify-center gap-1 font-display text-2xl font-bold text-amber-500">
                <DynoCoin className="h-6 w-6" /> +{result.coins_awarded}
              </p>
              <p className="text-xs text-muted">earned</p>
            </div>
            <div className="rounded-2xl bg-orange-500/10 px-5 py-3">
              <p className="font-display text-2xl font-bold text-orange-500">
                {result.current_streak}
              </p>
              <p className="text-xs text-muted">🔥 streak</p>
            </div>
          </div>
          <Link to="/games">
            <Button className="mt-6 px-6 py-3">Back to arcade</Button>
          </Link>
        </Card>
      </main>
    )
  }

  // Pool is derived: every tile not yet placed in a locked group.
  const lockedTiles = new Set(locked.flat())
  const tiles = data.tiles.filter((t) => !lockedTiles.has(t))

  const toggle = (tile: string) =>
    setSelected((prev) =>
      prev.includes(tile)
        ? prev.filter((t) => t !== tile)
        : prev.length < groupSize
          ? [...prev, tile]
          : prev,
    )

  const lockGroup = () => {
    if (selected.length !== groupSize) return
    setLocked((prev) => [...prev, selected])
    setSelected([])
  }

  const unlockGroup = (i: number) => setLocked((prev) => prev.filter((_, idx) => idx !== i))

  const submit = () => {
    const durationSeconds = startRef.current
      ? Math.floor((Date.now() - startRef.current) / 1000)
      : 0
    attempt.mutate(
      { groups: locked, durationSeconds },
      {
        onSuccess: (res) => {
          setResult(res)
          if (res.solved) celebrate()
        },
        onError: () => toast.error('Could not submit. Try again.'),
      },
    )
  }

  const mmss = (s: number) => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`

  const canSubmit = locked.length === groupCount

  return (
    <main className="mx-auto max-w-2xl">
      {crumb}
      <div className="mt-6 flex items-start justify-between gap-3">
        <div>
          <h1 className="font-display text-2xl font-bold text-fg">🧩 Connections</h1>
          <p className="mt-1 text-sm text-muted">
            Sort all 16 tiles into 4 hidden groups of {groupSize}, then submit.
          </p>
        </div>
        <div className="flex shrink-0 items-center gap-2">
          <span className="rounded-full bg-brand/10 px-3 py-1 text-xs font-semibold text-brand">
            {data.difficulty_label}
          </span>
          <span className="rounded-full border border-line px-3 py-1 font-mono text-xs font-semibold text-fg">
            ⏱ {mmss(elapsed)}
          </span>
        </div>
      </div>

      {/* Locked groups */}
      {locked.length > 0 && (
        <div className="mt-5 space-y-2.5">
          {locked.map((group, i) => (
            <button
              key={i}
              type="button"
              onClick={() => unlockGroup(i)}
              className="animate-pop-in flex w-full flex-wrap items-center justify-center gap-2 rounded-2xl border border-brand/40 bg-gradient-to-r from-brand/15 to-brand-2/15 px-3 py-3 text-center shadow-sm transition hover:border-brand"
              title="Tap to break this group up"
            >
              {group.map((tile) => (
                <span
                  key={tile}
                  className="rounded-lg bg-elevated px-3 py-1.5 text-sm font-semibold text-fg shadow-sm"
                >
                  {tile}
                </span>
              ))}
            </button>
          ))}
        </div>
      )}

      {/* Pool */}
      <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4">
        {tiles.map((tile) => {
          const active = selected.includes(tile)
          return (
            <button
              key={tile}
              type="button"
              onClick={() => toggle(tile)}
              className={`flex h-20 items-center justify-center rounded-2xl border px-2 text-center text-sm font-bold transition duration-150 ${
                active
                  ? 'scale-[1.03] border-brand bg-gradient-to-br from-brand to-brand-2 text-white shadow-lg shadow-brand/30'
                  : 'border-line bg-elevated text-fg shadow-sm hover:-translate-y-0.5 hover:border-brand/40 hover:shadow-md'
              }`}
            >
              {tile}
            </button>
          )
        })}
      </div>

      <div className="mt-6 flex items-center justify-between gap-3">
        <span className="text-sm text-muted">
          {locked.length}/{groupCount} groups locked
        </span>
        {canSubmit ? (
          <Button onClick={submit} disabled={attempt.isPending} className="px-7 py-3">
            {attempt.isPending ? 'Checking…' : 'Submit 🏁'}
          </Button>
        ) : (
          <Button onClick={lockGroup} disabled={selected.length !== groupSize} className="px-6 py-3">
            Lock group ({selected.length}/{groupSize})
          </Button>
        )}
      </div>
    </main>
  )
}
