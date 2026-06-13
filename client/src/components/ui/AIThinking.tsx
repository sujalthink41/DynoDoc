/** The shared "AI is working" indicator — a glowing orb, shimmering label, and
 *  staggered dots. Reused everywhere DynoDoc calls an LLM (intake, generation,
 *  quizzes, the in-lesson tutor). */
export function AIThinking({ label = 'DynoDoc is thinking…' }: { label?: string }) {
  return (
    <div className="inline-flex items-center gap-3 rounded-2xl border border-brand/15 bg-brand/5 px-4 py-2.5">
      <span className="animate-ai-glow flex h-7 w-7 items-center justify-center rounded-xl bg-gradient-to-br from-brand to-brand-2">
        <span className="font-display text-xs font-bold text-white">D</span>
      </span>
      <span className="text-shimmer-fast bg-gradient-to-r from-muted via-fg to-muted bg-clip-text text-sm font-medium text-transparent">
        {label}
      </span>
      <span className="flex items-end gap-1 pb-0.5">
        <span className="animate-ai-dot h-1.5 w-1.5 rounded-full bg-brand" />
        <span className="animate-ai-dot h-1.5 w-1.5 rounded-full bg-brand [animation-delay:0.15s]" />
        <span className="animate-ai-dot h-1.5 w-1.5 rounded-full bg-brand [animation-delay:0.3s]" />
      </span>
    </div>
  )
}
