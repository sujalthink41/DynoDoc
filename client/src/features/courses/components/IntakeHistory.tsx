import type { IntakeSummary } from '@/features/courses/types'
import { formatRelative } from '@/lib/relativeTime'

interface IntakeHistoryProps {
  items: IntakeSummary[]
  selectedId: string | null
  onSelect: (id: string) => void
  onNew: () => void
}

function PlusIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      className="h-4 w-4"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      aria-hidden
    >
      <path d="M12 5v14M5 12h14" />
    </svg>
  )
}

export function IntakeHistory({ items, selectedId, onSelect, onNew }: IntakeHistoryProps) {
  return (
    <aside className="hidden w-72 shrink-0 flex-col border-r border-line bg-surface/40 md:flex">
      <div className="flex items-center justify-between px-4 py-4">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-muted">Conversations</h2>
        <button
          type="button"
          onClick={onNew}
          className="flex items-center gap-1.5 rounded-full bg-gradient-to-r from-brand to-brand-2 px-3 py-1.5 text-xs font-semibold text-white shadow-sm transition hover:-translate-y-0.5"
        >
          <PlusIcon />
          New
        </button>
      </div>

      <div className="flex-1 space-y-1 overflow-y-auto px-2 pb-4">
        {items.length === 0 ? (
          <p className="px-3 py-6 text-center text-sm text-muted">
            No conversations yet. Start one to plan your first course.
          </p>
        ) : (
          items.map((item) => {
            const active = item.id === selectedId
            const ready = item.status === 'ready'
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => onSelect(item.id)}
                className={`group flex w-full flex-col gap-1 rounded-xl px-3 py-2.5 text-left transition ${
                  active ? 'bg-brand/10 ring-1 ring-brand/30' : 'hover:bg-elevated'
                }`}
              >
                <span
                  className={`line-clamp-1 text-sm font-medium ${active ? 'text-brand' : 'text-fg'}`}
                >
                  {item.goal}
                </span>
                <span className="flex items-center gap-2 text-xs text-muted">
                  <span
                    className={`h-1.5 w-1.5 rounded-full ${
                      ready ? 'bg-green-500' : 'bg-amber-400'
                    }`}
                  />
                  {ready ? 'Course ready' : 'In progress'}
                  <span className="text-muted/50">·</span>
                  {formatRelative(item.created_at)}
                </span>
              </button>
            )
          })
        )}
      </div>

      <p className="border-t border-line px-4 py-3 text-[0.7rem] leading-relaxed text-muted/70">
        Past conversations are read-only.
      </p>
    </aside>
  )
}
