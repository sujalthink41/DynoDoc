/** The shared "AI is working" indicator — reused for intake + generation. */
export function AIThinking({ label = 'DynoDoc is thinking…' }: { label?: string }) {
  return (
    <div className="flex items-center gap-3 rounded-2xl bg-brand/5 p-4 ring-1 ring-brand/20">
      <span className="h-4 w-4 animate-spin rounded-full border-2 border-brand/30 border-t-brand" />
      <p className="text-sm text-muted">{label}</p>
    </div>
  )
}
