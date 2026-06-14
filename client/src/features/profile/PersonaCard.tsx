import { useState } from 'react'
import { toast } from 'sonner'

import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { ProgressBar } from '@/components/ui/ProgressBar'
import { usePersona, useUpdatePersona } from '@/features/game/queries'

export function PersonaCard() {
  const { data } = usePersona(true)
  const update = useUpdatePersona()
  const [drafts, setDrafts] = useState<Record<string, string>>({})

  if (!data) return null

  const original: Record<string, string> = {}
  data.questions.forEach((q) => {
    original[q.key] = q.answer
  })
  const valueOf = (key: string) => (key in drafts ? drafts[key] : (original[key] ?? ''))
  const dirty = Object.entries(drafts).some(([k, v]) => v !== (original[k] ?? ''))
  const answered = data.questions.filter((q) => valueOf(q.key).trim()).length
  const percent = Math.round((answered / data.total) * 100)

  const choose = (key: string, opt: string) =>
    setDrafts((prev) => ({ ...prev, [key]: valueOf(key) === opt ? '' : opt }))

  const save = () =>
    update.mutate(drafts, {
      onSuccess: () => {
        setDrafts({})
        toast.success('Saved — thanks for sharing! 🎉')
      },
      onError: () => toast.error('Could not save. Try again.'),
    })

  return (
    <Card className="p-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="font-display text-xl font-semibold text-fg">About you 🎈</h2>
          <p className="mt-1 text-sm text-muted">
            A few fun questions — we use these to tailor DynoDoc to you. Fill them anytime.
          </p>
        </div>
        <div className="w-40">
          <div className="flex items-center justify-between text-xs">
            <span className="font-medium text-fg">{percent}% complete</span>
            <span className="text-muted">
              {answered}/{data.total}
            </span>
          </div>
          <ProgressBar value={percent} className="mt-1.5" />
        </div>
      </div>

      <div className="mt-6 space-y-5">
        {data.questions.map((q) => (
          <div key={q.key}>
            <p className="text-sm font-medium text-fg">
              <span className="mr-1.5">{q.emoji}</span>
              {q.prompt}
            </p>
            {q.kind === 'choice' ? (
              <>
                <div className="mt-2 flex flex-wrap gap-2">
                  {q.options.map((opt) => {
                    const active = valueOf(q.key) === opt
                    return (
                      <button
                        key={opt}
                        type="button"
                        onClick={() => choose(q.key, opt)}
                        className={`rounded-full border px-3.5 py-1.5 text-sm transition ${
                          active
                            ? 'border-brand bg-gradient-to-r from-brand to-brand-2 text-white shadow-sm'
                            : 'border-line text-muted hover:border-brand/40 hover:text-fg'
                        }`}
                      >
                        {opt}
                      </button>
                    )
                  })}
                </div>
                {q.allow_custom && (
                  <input
                    value={q.options.includes(valueOf(q.key)) ? '' : valueOf(q.key)}
                    onChange={(e) => setDrafts((prev) => ({ ...prev, [q.key]: e.target.value }))}
                    placeholder="…or type your own"
                    maxLength={60}
                    className="mt-2 w-full rounded-xl border border-line bg-surface px-4 py-2 text-sm text-fg placeholder:text-muted focus:border-brand/50 focus:outline-none"
                  />
                )}
              </>
            ) : (
              <input
                value={valueOf(q.key)}
                onChange={(e) => setDrafts((prev) => ({ ...prev, [q.key]: e.target.value }))}
                placeholder="Type your answer…"
                maxLength={120}
                className="mt-2 w-full rounded-xl border border-line bg-surface px-4 py-2.5 text-sm text-fg placeholder:text-muted focus:border-brand/50 focus:outline-none"
              />
            )}
          </div>
        ))}
      </div>

      <div className="mt-6 flex items-center justify-end gap-3">
        {dirty && <span className="text-xs text-muted">Unsaved changes</span>}
        <Button onClick={save} disabled={!dirty || update.isPending} className="px-6 py-2.5">
          {update.isPending ? 'Saving…' : 'Save'}
        </Button>
      </div>
    </Card>
  )
}
