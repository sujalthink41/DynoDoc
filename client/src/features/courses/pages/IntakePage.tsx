import { useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'

import { AIThinking } from '@/components/ui/AIThinking'
import { Button } from '@/components/ui/Button'
import { Spinner } from '@/components/ui/Spinner'
import { useAuth } from '@/features/auth/queries'
import { ChatBubble } from '@/features/courses/components/ChatBubble'
import { IntakeHistory } from '@/features/courses/components/IntakeHistory'
import { FREE_COURSE_LIMIT } from '@/features/courses/constants'
import {
  useAnswerIntake,
  useCourses,
  useCreateCourse,
  useIntakeHistory,
  useIntakeSession,
  useStartIntake,
} from '@/features/courses/queries'
import type { IntakeSession } from '@/features/courses/types'
import { useProfile } from '@/features/game/queries'
import { ApiError } from '@/lib/apiClient'

const SUGGESTIONS = [
  'Python for data analysis',
  'React + TypeScript',
  'System design basics',
  'Intro to machine learning',
]
const STORAGE_KEY = 'dynodoc:active-intake'
const MAX_COMPOSER_H = 112 // ~4 lines, then it scrolls

export function IntakePage() {
  const navigate = useNavigate()
  const auth = useAuth()
  const userInitial =
    auth.status === 'authenticated'
      ? (auth.user.display_name ?? auth.user.email).charAt(0).toUpperCase()
      : 'Y'

  const [liveSession, setLiveSession] = useState<IntakeSession | null>(null)
  const [viewingId, setViewingId] = useState<string | null>(null)
  const [resumeId, setResumeId] = useState<string | null>(() => localStorage.getItem(STORAGE_KEY))
  const [pendingUser, setPendingUser] = useState<string | null>(null)
  const [input, setInput] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const endRef = useRef<HTMLDivElement>(null)

  const history = useIntakeHistory()
  const viewing = useIntakeSession(viewingId)
  // Resume an unfinished chat across navigations (only while there's no live session).
  // Prefer the explicitly-remembered id, but fall back to the most recent unfinished
  // chat from history so resume still works after localStorage is cleared.
  const latestUnfinishedId =
    history.data?.find((s) => s.status === 'in_progress')?.id ?? null
  const effectiveResumeId = resumeId ?? latestUnfinishedId
  const resumed = useIntakeSession(liveSession ? null : effectiveResumeId)
  const { data: courses } = useCourses()
  const { data: player } = useProfile()
  const startIntake = useStartIntake()
  const answerIntake = useAnswerIntake()
  const createCourse = useCreateCourse()

  const courseLimit = FREE_COURSE_LIMIT + (player?.bonus_course_slots ?? 0)
  const atLimit = (courses?.length ?? 0) >= courseLimit
  const busy = startIntake.isPending || answerIntake.isPending
  const historyMode = viewingId !== null

  const activeSession = liveSession ?? (viewingId ? null : (resumed.data ?? null))
  const ready =
    !historyMode && activeSession?.status === 'ready' && activeSession.profile !== null
  const transcript = historyMode
    ? (viewing.data?.transcript ?? [])
    : (activeSession?.transcript ?? [])
  const resuming = !historyMode && !liveSession && effectiveResumeId !== null && resumed.isPending
  // True when we're showing a previously-started chat the user hasn't yet touched live.
  const isResumedView = !historyMode && !liveSession && pendingUser === null && resumed.data != null
  const hasConversation = transcript.length > 0 || pendingUser !== null

  const scrollEnd = () => requestAnimationFrame(() => endRef.current?.scrollIntoView())

  const resetComposer = () => {
    const el = textareaRef.current
    if (el) el.style.height = 'auto'
  }

  const grow = () => {
    const el = textareaRef.current
    if (el) {
      el.style.height = 'auto'
      el.style.height = `${Math.min(el.scrollHeight, MAX_COMPOSER_H)}px`
    }
  }

  const newChat = () => {
    setLiveSession(null)
    setViewingId(null)
    setResumeId(null)
    localStorage.removeItem(STORAGE_KEY)
    setPendingUser(null)
    setInput('')
    resetComposer()
  }

  const selectConversation = (id: string) => {
    if (id === liveSession?.id || id === activeSession?.id) {
      setViewingId(null) // it's the active chat — return to live mode
    } else {
      setViewingId(id)
    }
  }

  const send = (text: string) => {
    const trimmed = text.trim()
    if (!trimmed || busy || ready || historyMode) return
    setInput('')
    resetComposer()
    setPendingUser(trimmed)
    scrollEnd()
    const onSuccess = (session: IntakeSession) => {
      setLiveSession(session)
      setResumeId(session.id)
      localStorage.setItem(STORAGE_KEY, session.id)
      setPendingUser(null)
      scrollEnd()
    }
    const onError = () => setPendingUser(null)
    const targetId = liveSession?.id ?? activeSession?.id ?? null
    if (!targetId) {
      startIntake.mutate(trimmed, { onSuccess, onError })
    } else {
      answerIntake.mutate({ id: targetId, answer: trimmed }, { onSuccess, onError })
    }
  }

  const build = () => {
    const id = liveSession?.id ?? activeSession?.id
    if (!id) return
    createCourse.mutate(id, {
      onSuccess: (course) => {
        localStorage.removeItem(STORAGE_KEY)
        navigate(`/courses/${course.id}`)
      },
      onError: (error) => {
        if (error instanceof ApiError && error.code === 'course_limit_reached') {
          toast.error('Free plan limit reached. Unlock a slot with coins or upgrade. 🚀')
        } else {
          toast.error('Could not build your course. Try again.')
        }
      },
    })
  }

  const selectedId = viewingId ?? liveSession?.id ?? activeSession?.id ?? null

  return (
    <main className="flex h-full">
      <IntakeHistory
        items={history.data ?? []}
        selectedId={selectedId}
        onSelect={selectConversation}
        onNew={newChat}
      />

      <section className="flex flex-1 flex-col">
        <div className="scrollbar-none flex-1 overflow-y-auto">
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
            ) : resuming ? (
              <div className="flex justify-center py-20">
                <Spinner />
              </div>
            ) : !hasConversation ? (
              <div className="flex min-h-[60vh] flex-col items-center justify-center text-center">
                <span className="animate-float flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-brand to-brand-2 font-display text-3xl font-bold text-white shadow-xl shadow-brand/30">
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
                      className="rounded-full border border-line bg-surface px-4 py-2 text-sm text-muted transition hover:-translate-y-0.5 hover:border-brand/40 hover:text-fg"
                    >
                      {s}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="space-y-5">
                {isResumedView && !ready && (
                  <div className="flex flex-wrap items-center justify-between gap-2 rounded-xl border border-brand/30 bg-brand/5 px-4 py-3 text-sm">
                    <span className="text-muted">
                      ↩️ Picking up your unfinished chat about{' '}
                      <span className="font-medium text-fg">{resumed.data?.goal}</span>. Want a
                      different topic?
                    </span>
                    <button
                      type="button"
                      onClick={newChat}
                      className="shrink-0 rounded-full border border-line bg-surface px-3 py-1.5 text-xs font-medium text-fg transition hover:border-brand/40"
                    >
                      Start a new topic
                    </button>
                  </div>
                )}
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
                {ready && atLimit && (
                  <div className="ml-11 mt-2 rounded-2xl border border-line bg-surface px-4 py-3 text-sm text-muted">
                    🔒 You've used all {courseLimit} course slots. You can still chat and explore —
                    unlock a slot with coins on your dashboard, or upgrade to Pro to build this one.
                  </div>
                )}
                {ready && !atLimit && (
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
                className="flex items-end gap-2 rounded-2xl border border-line bg-surface p-2 shadow-sm transition focus-within:border-brand/50"
              >
                <textarea
                  ref={textareaRef}
                  value={input}
                  onChange={(e) => {
                    setInput(e.target.value)
                    grow()
                  }}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault()
                      send(input)
                    }
                  }}
                  rows={1}
                  placeholder={activeSession ? 'Type your answer…  (Shift+Enter for a new line)' : 'e.g. I want to learn Python'}
                  disabled={busy}
                  className="scrollbar-none max-h-28 flex-1 resize-none bg-transparent px-3 py-2 text-fg placeholder:text-muted focus:outline-none disabled:opacity-60"
                />
                <Button
                  type="submit"
                  disabled={busy || !input.trim()}
                  className="h-10 w-10 shrink-0 rounded-xl p-0"
                  aria-label="Send"
                >
                  ↑
                </Button>
              </form>
            )}
          </div>
        </div>
      </section>
    </main>
  )
}
