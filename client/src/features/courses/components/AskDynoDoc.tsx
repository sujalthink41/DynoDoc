import { useEffect, useRef, useState } from 'react'
import { toast } from 'sonner'

import { AIThinking } from '@/components/ui/AIThinking'
import { Button } from '@/components/ui/Button'
import { ChatBubble } from '@/features/courses/components/ChatBubble'
import { useAskTutor } from '@/features/courses/queries'
import type { TutorTurn } from '@/features/courses/types'

interface AskDynoDocProps {
  lectureId: string
  topicIndex: number | null
  topicLabel?: string
  /** True once the lesson is generated — only then can it be asked about. */
  enabled: boolean
  userInitial?: string
  /** A snippet the learner selected in the lesson to ask about (ChatGPT-style). */
  quote?: string | null
  onClearQuote?: () => void
  /** Shown on small screens to close the slide-over. */
  onClose?: () => void
}

const STARTERS = ['Explain this more simply', 'Give me an example', 'Why does this matter?']
const MAX_CHARS = 500

export function AskDynoDoc({
  lectureId,
  topicIndex,
  topicLabel,
  enabled,
  userInitial,
  quote,
  onClearQuote,
  onClose,
}: AskDynoDocProps) {
  const [turns, setTurns] = useState<TutorTurn[]>([])
  const [input, setInput] = useState('')
  const ask = useAskTutor(lectureId)

  const scrollRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  // Scroll ONLY the messages container (never the window) so opening the panel
  // can't smooth-scroll the whole page.
  useEffect(() => {
    const el = scrollRef.current
    if (el) el.scrollTop = el.scrollHeight
  }, [turns.length, ask.isPending])

  // When the learner quotes a selection, focus the composer so they can type.
  useEffect(() => {
    if (quote) inputRef.current?.focus()
  }, [quote])

  const canAsk = enabled && topicIndex !== null

  const send = (text: string) => {
    const question = text.trim()
    if (!question || ask.isPending || !canAsk) return
    setInput('')
    // A quoted snippet is shown to the learner and prepended for the model.
    const apiQuestion = quote
      ? `Regarding this part of the lesson:\n"""${quote}"""\n\n${question}`
      : question
    const shown = quote ? `“${quote.length > 140 ? `${quote.slice(0, 140)}…` : quote}”\n\n${question}` : question
    onClearQuote?.()
    const history = turns
    setTurns((prev) => [...prev, { role: 'user', content: shown }])
    ask.mutate(
      { topicIndex, question: apiQuestion, history },
      {
        onSuccess: (reply) =>
          setTurns((prev) => [...prev, { role: 'assistant', content: reply.answer }]),
        onError: () => {
          toast.error('Could not reach the tutor. Try again.')
          setTurns((prev) => prev.slice(0, -1)) // drop the optimistic question
        },
      },
    )
  }

  return (
    <div className="flex h-full flex-col bg-surface/40">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-line px-4 py-3">
        <div className="flex min-w-0 items-center gap-2.5">
          <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-brand to-brand-2 font-display text-sm font-bold text-white shadow-md shadow-brand/30">
            D
          </span>
          <div className="min-w-0">
            <p className="text-sm font-semibold text-fg">Ask DynoDoc</p>
            <p className="truncate text-xs text-muted">
              {topicLabel ? `About: ${topicLabel}` : 'Your lesson tutor'}
            </p>
          </div>
        </div>
        {onClose && (
          <button
            type="button"
            onClick={onClose}
            aria-label="Close chat"
            className="rounded-lg p-1.5 text-muted transition hover:bg-elevated hover:text-fg"
          >
            ✕
          </button>
        )}
      </div>

      {/* Messages */}
      <div ref={scrollRef} className="scrollbar-none flex-1 space-y-4 overflow-y-auto px-4 py-5">
        {!canAsk ? (
          <div className="flex h-full flex-col items-center justify-center px-4 text-center">
            <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-brand to-brand-2 font-display text-xl font-bold text-white shadow-lg shadow-brand/30">
              D
            </span>
            <p className="mt-4 text-sm font-medium text-fg">
              {topicIndex === null ? 'Pick a lesson to start' : 'Generate this lesson first'}
            </p>
            <p className="mt-1 text-xs text-muted">
              {topicIndex === null
                ? 'Select a lesson on the left and I’ll answer questions about it.'
                : 'Once the lesson is written, ask me anything about it.'}
            </p>
          </div>
        ) : turns.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center px-2 text-center">
            <p className="text-sm text-muted">Ask anything about this lesson 👇</p>
            <div className="mt-4 flex flex-wrap justify-center gap-2">
              {STARTERS.map((s) => (
                <button
                  key={s}
                  type="button"
                  onClick={() => send(s)}
                  className="rounded-full border border-line bg-surface px-3.5 py-1.5 text-xs text-muted transition hover:border-brand/40 hover:text-fg"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        ) : (
          turns.map((turn, i) => (
            <ChatBubble
              key={i}
              role={turn.role}
              content={turn.content}
              userInitial={userInitial}
              markdown
            />
          ))
        )}
        {ask.isPending && (
          <div className="pl-11">
            <AIThinking label="DynoDoc is thinking…" />
          </div>
        )}
      </div>

      {/* Composer */}
      <form
        onSubmit={(e) => {
          e.preventDefault()
          send(input)
        }}
        className="border-t border-line p-3"
      >
        {quote && (
          <div className="mb-2 flex items-start gap-2 rounded-xl border-l-2 border-brand bg-brand/5 px-3 py-2">
            <span className="line-clamp-2 flex-1 text-xs italic text-muted">“{quote}”</span>
            <button
              type="button"
              onClick={onClearQuote}
              aria-label="Remove quote"
              className="shrink-0 text-xs text-muted transition hover:text-fg"
            >
              ✕
            </button>
          </div>
        )}
        <div className="flex items-center gap-2 rounded-2xl border border-line bg-surface p-1.5 focus-within:border-brand/50">
          <input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            maxLength={MAX_CHARS}
            placeholder={
              quote
                ? 'Ask about the selected text…'
                : canAsk
                  ? 'Ask about this lesson…'
                  : 'Open a generated lesson to ask…'
            }
            disabled={!canAsk || ask.isPending}
            className="flex-1 bg-transparent px-3 py-1.5 text-sm text-fg placeholder:text-muted focus:outline-none disabled:cursor-not-allowed"
          />
          <Button
            type="submit"
            disabled={!canAsk || ask.isPending || !input.trim()}
            className="px-4 py-2 text-sm"
          >
            Ask
          </Button>
        </div>
        {input.length >= MAX_CHARS - 80 && (
          <p
            className={`mt-1 pr-2 text-right text-[0.7rem] ${
              input.length >= MAX_CHARS ? 'text-brand' : 'text-muted'
            }`}
          >
            {input.length}/{MAX_CHARS}
          </p>
        )}
      </form>
    </div>
  )
}
