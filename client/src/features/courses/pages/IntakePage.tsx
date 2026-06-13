import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { AIThinking } from '@/components/ui/AIThinking'
import { Button } from '@/components/ui/Button'
import { Spinner } from '@/components/ui/Spinner'
import { useAuth } from '@/features/auth/queries'
import { ChatBubble } from '@/features/courses/components/ChatBubble'
import { IntakeHistory } from '@/features/courses/components/IntakeHistory'
import {
  useAnswerIntake,
  useCreateCourse,
  useIntakeHistory,
  useIntakeSession,
  useStartIntake,
} from '@/features/courses/queries'
import type { IntakeSession } from '@/features/courses/types'

const SUGGESTIONS = [
  'Python for data analysis',
  'React + TypeScript',
  'System design basics',
  'Intro to machine learning',
]

export function IntakePage() {
  const navigate = useNavigate()
  const auth = useAuth()
  const userInitial =
    auth.status === 'authenticated'
      ? (auth.user.display_name ?? auth.user.email).charAt(0).toUpperCase()
      : 'Y'

  const [liveSession, setLiveSession] = useState<IntakeSession | null>(null)
  const [viewingId, setViewingId] = useState<string | null>(null)
  const [pendingUser, setPendingUser] = useState<string | null>(null)
  const [input, setInput] = useState('')

  const history = useIntakeHistory()
  const viewing = useIntakeSession(viewingId)
  const startIntake = useStartIntake()
  const answerIntake = useAnswerIntake()
  const createCourse = useCreateCourse()

  const busy = startIntake.isPending || answerIntake.isPending
  const historyMode = viewingId !== null
  const ready =
    !historyMode && liveSession?.status === 'ready' && liveSession.profile !== null

  const transcript = historyMode
    ? (viewing.data?.transcript ?? [])
    : (liveSession?.transcript ?? [])
  const hasConversation = transcript.length > 0 || pendingUser !== null

  const endRef = useRef<HTMLDivElement>(null)
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [transcript.length, pendingUser, busy, historyMode])

  const newChat = () => {
    setLiveSession(null)
    setViewingId(null)
    setPendingUser(null)
    setInput('')
  }

  const selectConversation = (id: string) => {
    if (liveSession && id === liveSession.id) {
      setViewingId(null) // it's the active chat — return to live mode
    } else {
      setViewingId(id)
    }
  }

  const send = (text: string) => {
    const trimmed = text.trim()
    if (!trimmed || busy || ready || historyMode) return
    setInput('')
    setPendingUser(trimmed)
    const onSuccess = (session: IntakeSession) => {
      setLiveSession(session)
      setPendingUser(null)
    }
    const onError = () => setPendingUser(null)
    if (!liveSession) {
      startIntake.mutate(trimmed, { onSuccess, onError })
    } else {
      answerIntake.mutate({ id: liveSession.id, answer: trimmed }, { onSuccess, onError })
    }
  }

  const build = () => {
    if (!liveSession) return
    createCourse.mutate(liveSession.id, {
      onSuccess: (course) => navigate(`/courses/${course.id}`),
    })
  }

  const selectedId = viewingId ?? liveSession?.id ?? null

  return (
    <main className="flex h-[calc(100vh-57px)]">
      <IntakeHistory
        items={history.data ?? []}
        selectedId={selectedId}
        onSelect={selectConversation}
        onNew={newChat}
      />

      <section className="flex flex-1 flex-col">
        <div className="flex-1 overflow-y-auto">
          <div className="mx-auto max-w-2xl px-6 py-8">
            {historyMode ? (
              viewing.isPending ? (
                <div className="flex justify-center py-20">
                  <Spinner />
                </div>
              ) : (
                <>
                  <div className="mb-6 rounded-xl border border-line bg-surface/60 px-4 py-3 text-center text-sm text-muted">
                    📖 Viewing a past conversation · read-only
                  </div>
                  <div className="space-y-5">
                    {transcript.map((turn, i) => (
                      <ChatBubble
                        key={i}
                        role={turn.role}
                        content={turn.content}
                        userInitial={userInitial}
                      />
                    ))}
                  </div>
                </>
              )
            ) : !hasConversation ? (
              <div className="flex min-h-[60vh] flex-col items-center justify-center text-center">
                <span className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-brand to-brand-2 font-display text-2xl font-bold text-white shadow-lg shadow-brand/30">
                  D
                </span>
                <h1 className="mt-6 font-display text-3xl font-bold text-fg sm:text-4xl">
                  What do you want to learn?
                </h1>
                <p className="mt-3 max-w-md text-muted">
                  Tell me a <span className="font-medium text-fg">technical</span> topic — I'll ask
                  a few quick questions, then build a course just for you.
                </p>
                <div className="mt-7 flex flex-wrap justify-center gap-2">
                  {SUGGESTIONS.map((s) => (
                    <button
                      key={s}
                      type="button"
                      onClick={() => send(s)}
                      className="rounded-full border border-line bg-surface px-4 py-2 text-sm text-muted transition hover:border-brand/40 hover:text-fg"
                    >
                      {s}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="space-y-5">
                {transcript.map((turn, i) => (
                  <ChatBubble
                    key={i}
                    role={turn.role}
                    content={turn.content}
                    userInitial={userInitial}
                  />
                ))}
                {pendingUser && (
                  <ChatBubble role="user" content={pendingUser} userInitial={userInitial} />
                )}
                {busy && (
                  <div className="pl-11">
                    <AIThinking label="DynoDoc is thinking…" />
                  </div>
                )}
                {ready && (
                  <div className="pl-11 pt-2">
                    <Button onClick={build} disabled={createCourse.isPending} className="px-6 py-3">
                      {createCourse.isPending ? 'Building your course…' : '✨ Build my course'}
                    </Button>
                  </div>
                )}
              </div>
            )}
            <div ref={endRef} />
          </div>
        </div>

        {/* Composer / read-only footer */}
        <div className="border-t border-line bg-elevated/60 px-6 py-4 backdrop-blur">
          <div className="mx-auto max-w-2xl">
            {historyMode ? (
              <Button variant="ghost" onClick={newChat} className="w-full px-6 py-3">
                + Start a new conversation
              </Button>
            ) : ready ? (
              <p className="text-center text-sm text-muted">
                All set — build your course above to get started. 🎉
              </p>
            ) : (
              <form
                onSubmit={(e) => {
                  e.preventDefault()
                  send(input)
                }}
                className="flex items-center gap-2 rounded-2xl border border-line bg-surface p-2 shadow-sm focus-within:border-brand/50"
              >
                <input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder={liveSession ? 'Type your answer…' : 'e.g. I want to learn Python'}
                  disabled={busy}
                  className="flex-1 bg-transparent px-3 py-2 text-fg placeholder:text-muted focus:outline-none"
                />
                <Button type="submit" disabled={busy || !input.trim()} className="px-5 py-2.5">
                  Send
                </Button>
              </form>
            )}
          </div>
        </div>
      </section>
    </main>
  )
}
