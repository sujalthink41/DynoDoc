import { Link } from 'react-router-dom'

import type { LectureSummary } from '@/features/courses/types'

type NodeState = 'done' | 'current' | 'locked'

function isDone(lecture: LectureSummary): boolean {
  return lecture.lessons_total > 0 && lecture.lessons_passed >= lecture.lessons_total
}

/** A circular progress dial showing lessons passed / total for a module. */
function ProgressRing({ value, center }: { value: number; center: string }) {
  const r = 20
  const circ = 2 * Math.PI * r
  return (
    <svg viewBox="0 0 48 48" className="h-12 w-12 shrink-0">
      <circle cx="24" cy="24" r={r} fill="none" style={{ stroke: 'var(--line)' }} strokeWidth="5" />
      <circle
        cx="24"
        cy="24"
        r={r}
        fill="none"
        stroke="url(#dyno-ring)"
        strokeWidth="5"
        strokeLinecap="round"
        strokeDasharray={circ}
        strokeDashoffset={circ * (1 - value / 100)}
        transform="rotate(-90 24 24)"
      />
      <text
        x="24"
        y="24"
        textAnchor="middle"
        dominantBaseline="central"
        style={{ fill: 'var(--fg)' }}
        className="text-[9px] font-bold"
      >
        {center}
      </text>
    </svg>
  )
}

const LEVEL_CHIP: Record<NodeState, string> = {
  done: 'bg-amber-400/15 text-amber-500',
  current: 'bg-brand/15 text-brand',
  locked: 'bg-surface text-muted',
}

function ModuleCard({
  lecture,
  level,
  state,
}: {
  lecture: LectureSummary
  level: number
  state: NodeState
}) {
  const pct =
    lecture.lessons_total > 0
      ? Math.round((lecture.lessons_passed / lecture.lessons_total) * 100)
      : 0
  const cta = state === 'done' ? 'Review' : state === 'current' ? 'Continue' : 'Preview'

  return (
    <Link
      to={`/lectures/${lecture.id}`}
      className={`group block rounded-3xl border bg-elevated/70 p-5 shadow-xl backdrop-blur-xl transition duration-300 hover:-translate-y-1 ${
        state === 'current'
          ? 'border-brand/40 shadow-brand/15'
          : 'border-line hover:border-brand/30'
      }`}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <span
            className={`inline-block rounded-full px-2.5 py-0.5 text-[0.65rem] font-bold uppercase tracking-wider ${LEVEL_CHIP[state]}`}
          >
            Level {level}
          </span>
          <h3 className="mt-2 font-display text-lg font-semibold text-fg">{lecture.title}</h3>
          <p className="mt-1 line-clamp-2 text-sm text-muted">{lecture.summary}</p>
        </div>
        <ProgressRing value={pct} center={`${lecture.lessons_passed}/${lecture.lessons_total}`} />
      </div>

      <div className="mt-4 flex items-center justify-between gap-3">
        <div className="flex flex-wrap gap-1.5">
          {lecture.topics.slice(0, 2).map((topic) => (
            <span
              key={topic}
              className="rounded-full bg-brand/10 px-2.5 py-1 text-xs font-medium text-brand"
            >
              {topic}
            </span>
          ))}
          {lecture.topics.length > 2 && (
            <span className="rounded-full bg-surface px-2.5 py-1 text-xs text-muted">
              +{lecture.topics.length - 2}
            </span>
          )}
        </div>
        <span className="shrink-0 text-sm font-semibold text-brand opacity-0 transition group-hover:opacity-100">
          {cta} →
        </span>
      </div>
    </Link>
  )
}

export function LearningPath({ lectures }: { lectures: LectureSummary[] }) {
  // "Current" = the first module that isn't fully completed.
  const currentIndex = lectures.findIndex((l) => !isDone(l))

  return (
    <div className="relative mx-auto max-w-5xl">
      {/* shared ring gradient + ambient glow */}
      <svg className="absolute h-0 w-0" aria-hidden>
        <defs>
          <linearGradient id="dyno-ring" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#ef4444" />
            <stop offset="100%" stopColor="#f43f5e" />
          </linearGradient>
        </defs>
      </svg>
      <div
        aria-hidden
        className="animate-blob pointer-events-none absolute -left-24 top-10 h-72 w-72 rounded-full bg-brand/15 blur-3xl"
      />
      <div
        aria-hidden
        className="animate-blob animation-delay-2000 pointer-events-none absolute -right-24 top-1/2 h-72 w-72 rounded-full bg-brand-2/15 blur-3xl"
      />

      {/* The glowing journey spine */}
      <span
        aria-hidden
        className="absolute bottom-4 left-5 top-4 w-0.5 bg-gradient-to-b from-brand/50 via-line to-line md:left-1/2 md:-translate-x-1/2"
      />

      <ol className="relative space-y-10">
        {lectures.map((lecture, i) => {
          const state: NodeState = isDone(lecture)
            ? 'done'
            : i === currentIndex
              ? 'current'
              : 'locked'
          const onLeft = i % 2 === 0
          return (
            <li key={lecture.id} className="relative pl-16 md:pl-0">
              {/* Node marker on the spine */}
              <span
                className={`absolute left-5 top-5 z-10 flex h-11 w-11 -translate-x-1/2 items-center justify-center rounded-full text-sm font-bold ring-4 ring-bg md:left-1/2 ${
                  state === 'done'
                    ? 'bg-gradient-to-br from-amber-400 to-amber-500 text-white shadow-lg shadow-amber-500/40'
                    : state === 'current'
                      ? 'animate-ai-glow bg-gradient-to-br from-brand to-brand-2 text-white'
                      : 'border border-line bg-elevated text-muted/60'
                }`}
              >
                {state === 'done' ? '✓' : state === 'locked' ? '🔒' : i + 1}
              </span>

              {/* Card — alternates sides on desktop, stacks right on mobile */}
              <div className={`md:flex ${onLeft ? 'md:justify-start' : 'md:justify-end'}`}>
                <div className="md:w-[calc(50%-3rem)]">
                  <ModuleCard lecture={lecture} level={i + 1} state={state} />
                </div>
              </div>
            </li>
          )
        })}
      </ol>
    </div>
  )
}
