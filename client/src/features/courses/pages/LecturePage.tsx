import { type RefObject, useEffect, useRef, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { useParams } from 'react-router-dom'
import remarkGfm from 'remark-gfm'
import { toast } from 'sonner'

import { AIThinking } from '@/components/ui/AIThinking'
import { Breadcrumb, HomeIcon } from '@/components/ui/Breadcrumb'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { DynoCoin } from '@/components/ui/DynoCoin'
import { Spinner } from '@/components/ui/Spinner'
import { useAuth } from '@/features/auth/queries'
import { AskDynoDoc } from '@/features/courses/components/AskDynoDoc'
import { QuizPanel } from '@/features/courses/components/QuizPanel'
import { LESSON_UNLOCK_COST } from '@/features/game/constants'
import { useProfile } from '@/features/game/queries'
import {
  useGenerateReferences,
  useGenerateTopic,
  useLecture,
  useUnlockTopic,
} from '@/features/courses/queries'
import type { DocView, LessonState, ReferenceView } from '@/features/courses/types'
import { ApiError } from '@/lib/apiClient'

function ReferenceLink({ reference }: { reference: ReferenceView }) {
  return (
    <a
      href={reference.url}
      target="_blank"
      rel="noreferrer"
      className="flex items-center gap-3 rounded-xl border border-line bg-surface px-4 py-3 transition hover:border-brand/40"
    >
      <span className="text-lg">{reference.type === 'youtube' ? '▶️' : '📄'}</span>
      <span className="truncate text-sm text-fg">{reference.title}</span>
    </a>
  )
}

function ChatIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      className="h-6 w-6"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
    >
      <path d="M21 11.5a8.38 8.38 0 0 1-8.5 8.5 8.5 8.5 0 0 1-3.8-.9L3 21l1.9-5.7a8.5 8.5 0 0 1-.9-3.8 8.38 8.38 0 0 1 8.5-8.5 8.5 8.5 0 0 1 8.5 8.5Z" />
    </svg>
  )
}

/** Floating "Ask DynoDoc" pill shown when the learner selects text in the lesson. */
function SelectionAsk({
  targetRef,
  onAsk,
}: {
  targetRef: RefObject<HTMLElement | null>
  onAsk: (text: string) => void
}) {
  const [pos, setPos] = useState<{ top: number; left: number; text: string } | null>(null)

  useEffect(() => {
    const clear = () => setPos(null)
    const onUp = () => {
      const sel = window.getSelection()
      const el = targetRef.current
      if (!sel || sel.isCollapsed || !el || !sel.anchorNode || !el.contains(sel.anchorNode)) {
        return clear()
      }
      const text = sel.toString().trim()
      if (text.length < 2) return clear()
      const rect = sel.getRangeAt(0).getBoundingClientRect()
      setPos({ top: rect.top, left: rect.left + rect.width / 2, text })
    }
    document.addEventListener('mouseup', onUp)
    document.addEventListener('scroll', clear, true)
    return () => {
      document.removeEventListener('mouseup', onUp)
      document.removeEventListener('scroll', clear, true)
    }
  }, [targetRef])

  if (!pos) return null
  return (
    <button
      type="button"
      style={{
        position: 'fixed',
        top: pos.top - 10,
        left: pos.left,
        transform: 'translate(-50%, -100%)',
      }}
      // onMouseDown (not onClick) + preventDefault keeps the text selection alive.
      onMouseDown={(e) => {
        e.preventDefault()
        onAsk(pos.text)
        setPos(null)
        window.getSelection()?.removeAllRanges()
      }}
      className="animate-pop-up relative z-50 flex items-center gap-2 rounded-xl bg-fg px-3 py-2 text-xs font-semibold text-bg shadow-2xl ring-1 ring-black/5"
    >
      <span className="flex h-5 w-5 items-center justify-center rounded-md bg-gradient-to-br from-brand to-brand-2 text-white">
        <svg viewBox="0 0 24 24" className="h-3 w-3" fill="currentColor" aria-hidden>
          <path d="M12 2l1.7 5.3a3 3 0 0 0 1.9 1.9L21 11l-5.4 1.8a3 3 0 0 0-1.9 1.9L12 20l-1.7-5.3a3 3 0 0 0-1.9-1.9L3 11l5.4-1.8a3 3 0 0 0 1.9-1.9z" />
        </svg>
      </span>
      Ask DynoDoc
      <span className="absolute left-1/2 top-full h-2.5 w-2.5 -translate-x-1/2 -translate-y-1.5 rotate-45 bg-fg" />
    </button>
  )
}

function LessonBadge({ lesson }: { lesson: LessonState }) {
  if (lesson.passed) {
    return (
      <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-green-500 text-[10px] font-bold text-white">
        ✓
      </span>
    )
  }
  if (!lesson.unlocked) {
    return <span className="flex h-5 w-5 shrink-0 items-center justify-center text-xs">🔒</span>
  }
  return (
    <span
      className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-[10px] font-bold ${
        lesson.generated ? 'bg-brand text-white' : 'ring-1 ring-line'
      }`}
    >
      {lesson.index + 1}
    </span>
  )
}

export function LecturePage() {
  const { lectureId = '' } = useParams()
  const auth = useAuth()
  const userInitial =
    auth.status === 'authenticated'
      ? (auth.user.display_name ?? auth.user.email).charAt(0).toUpperCase()
      : 'Y'

  const { data: lecture, isPending } = useLecture(lectureId)
  const { data: player } = useProfile()
  const generateTopic = useGenerateTopic(lectureId)
  const generateReferences = useGenerateReferences(lectureId)
  const unlockTopic = useUnlockTopic(lectureId)
  const [selected, setSelected] = useState<number | null>(null)
  const [chatOpen, setChatOpen] = useState(false)
  const [navOpen, setNavOpen] = useState(false) // lessons drawer on small screens
  const [quote, setQuote] = useState<string | null>(null)
  const proseRef = useRef<HTMLDivElement>(null)

  if (isPending) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <Spinner />
      </div>
    )
  }
  if (!lecture) {
    return <p className="mx-auto max-w-3xl px-6 py-16 text-muted">Lecture not found.</p>
  }

  const docFor = (index: number): DocView | undefined =>
    lecture.docs.find((doc) => doc.position === index + 1)
  const generatingIndex = generateTopic.isPending ? generateTopic.variables : null

  const generate = (index: number) => {
    generateTopic.mutate(index, {
      onError: (error) => {
        if (error instanceof ApiError && error.code === 'lesson_locked') {
          toast.error('Pass the previous lesson’s quiz to unlock this lesson.')
        } else {
          toast.error('Could not generate this lesson. Try again.')
        }
      },
    })
  }

  const selectLesson = (lesson: LessonState) => {
    setQuote(null) // a quote from the previous lesson shouldn't carry over
    setSelected(lesson.index)
    setNavOpen(false) // close the lessons drawer after picking (mobile)
    // Locked lessons open to an unlock card instead of generating.
    if (lesson.unlocked && !docFor(lesson.index) && generateTopic.variables !== lesson.index) {
      generate(lesson.index)
    }
  }

  const unlockAndGenerate = (index: number) => {
    unlockTopic.mutate(index, {
      onSuccess: () => generate(index),
      onError: (error) => {
        if (error instanceof ApiError && error.code === 'insufficient_coins') {
          toast.error('Not enough DynoCoins — play Connections or pass quizzes to earn more.')
        } else {
          toast.error('Could not unlock this lesson. Try again.')
        }
      },
    })
  }

  const askAboutSelection = (text: string) => {
    setQuote(text)
    setChatOpen(true) // surfaces the chat on small screens; harmless on desktop
  }

  const selectedDoc = selected !== null ? docFor(selected) : undefined
  const selectedLesson =
    selected !== null ? lecture.lessons.find((l) => l.index === selected) : undefined
  const passedCount = lecture.lessons.filter((l) => l.passed).length

  const chat = (
    <AskDynoDoc
      key={`chat-${selected}`}
      lectureId={lectureId}
      topicIndex={selected}
      topicLabel={selectedLesson?.topic}
      enabled={Boolean(selectedDoc)}
      userInitial={userInitial}
      quote={quote}
      onClearQuote={() => setQuote(null)}
      onClose={() => setChatOpen(false)}
    />
  )

  const lessonsNav = (
    <>
      <div className="px-4 py-4">
        <p className="text-xs uppercase tracking-wider text-brand">Lecture {lecture.position}</p>
        <h2 className="mt-1 font-display text-lg font-bold leading-snug text-fg">{lecture.title}</h2>
        <p className="mt-2 text-xs font-medium text-muted">
          {passedCount}/{lecture.lessons.length} lessons passed
        </p>
      </div>
      <nav className="space-y-1 px-2 pb-4">
        {lecture.lessons.map((lesson) => {
          const active = selected === lesson.index
          return (
            <button
              key={lesson.index}
              type="button"
              onClick={() => selectLesson(lesson)}
              className={`flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm transition ${
                active
                  ? 'bg-brand/10 text-brand ring-1 ring-brand/20'
                  : lesson.unlocked
                    ? 'text-muted hover:bg-elevated hover:text-fg'
                    : 'text-muted/60'
              }`}
            >
              <LessonBadge lesson={lesson} />
              <span className="line-clamp-2">{lesson.topic}</span>
            </button>
          )
        })}
      </nav>
    </>
  )

  return (
    <div className="relative flex h-full flex-col overflow-hidden">
      {/* Top bar */}
      <header className="flex shrink-0 items-center gap-3 border-b border-line px-5 py-2.5">
        <button
          type="button"
          onClick={() => setNavOpen(true)}
          aria-label="Open lessons"
          className="flex items-center gap-1.5 rounded-lg border border-line px-2.5 py-1.5 text-xs font-medium text-muted transition hover:text-fg md:hidden"
        >
          ☰ Lessons
        </button>
        <Breadcrumb
          items={[
            { label: 'Home', to: '/app', icon: <HomeIcon /> },
            { label: lecture.course_title, to: `/courses/${lecture.course_id}` },
            { label: lecture.title },
          ]}
        />
      </header>

      <div className="relative flex min-h-0 flex-1 overflow-hidden">
        {/* Lessons nav (static, md+) */}
        <aside className="scrollbar-none hidden w-72 shrink-0 flex-col overflow-y-auto border-r border-line bg-surface/40 md:flex">
          {lessonsNav}
        </aside>

        {/* Lesson content — left-anchored; on lg it reserves room so the chat sits beside it */}
        <section
          className={`scrollbar-none flex-1 overflow-y-auto ${chatOpen ? 'lg:pr-[24rem]' : ''}`}
        >
          <div className="max-w-4xl px-6 py-8 sm:px-10">
            {selected === null ? (
              <div className="flex min-h-[60vh] flex-col items-center justify-center text-center">
                <h2 className="font-display text-2xl font-bold text-fg">{lecture.title}</h2>
                <p className="mt-2 max-w-md text-muted">{lecture.summary}</p>
                <p className="mt-6 text-sm text-muted">← Pick a lesson to start learning.</p>
              </div>
            ) : generatingIndex === selected ? (
              <div className="pt-10">
                <AIThinking label="Writing this lesson… a few seconds" />
              </div>
            ) : selectedDoc ? (
              <>
                <div
                  ref={proseRef}
                  className="prose prose-slate max-w-none dark:prose-invert prose-headings:font-display prose-a:text-brand"
                >
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{selectedDoc.content}</ReactMarkdown>
                </div>
                {selectedLesson && (
                  <QuizPanel key={selected} lectureId={lectureId} lesson={selectedLesson} />
                )}

                <section className="mt-12 border-t border-line pt-8">
                  <h2 className="font-display text-lg font-semibold text-fg">Go deeper</h2>
                  {lecture.references.length > 0 ? (
                    <div className="mt-4 grid gap-3 sm:grid-cols-2">
                      {lecture.references.map((reference) => (
                        <ReferenceLink key={reference.id} reference={reference} />
                      ))}
                    </div>
                  ) : generateReferences.isPending ? (
                    <div className="mt-4">
                      <AIThinking label="Finding the best articles & videos…" />
                    </div>
                  ) : (
                    <Button
                      variant="ghost"
                      onClick={() => generateReferences.mutate()}
                      className="mt-4 px-5 py-2.5"
                    >
                      🔎 Find resources for this lecture
                    </Button>
                  )}
                </section>
              </>
            ) : selectedLesson && !selectedLesson.unlocked ? (
              <Card className="p-10 text-center">
                <span className="text-4xl">🔒</span>
                <h3 className="mt-3 font-display text-xl font-semibold text-fg">
                  This lesson is locked
                </h3>
                <p className="mx-auto mt-2 max-w-md text-muted">
                  Pass the previous lesson’s quiz to unlock it the normal way — or jump ahead now by
                  spending DynoCoins. (You’ll still need the quiz to complete it.)
                </p>
                <Button
                  onClick={() => unlockAndGenerate(selected)}
                  disabled={unlockTopic.isPending || generateTopic.variables === selected}
                  className="mt-6 gap-1.5 px-6 py-3"
                >
                  {unlockTopic.isPending ? (
                    'Unlocking…'
                  ) : (
                    <>
                      Unlock for {LESSON_UNLOCK_COST} <DynoCoin className="h-4 w-4" />
                    </>
                  )}
                </Button>
                <p className="mt-3 flex items-center justify-center gap-1 text-xs text-muted">
                  You have <DynoCoin className="h-3.5 w-3.5" /> {player?.coins ?? 0} · earn more by
                  playing Connections &amp; passing quizzes.
                </p>
              </Card>
            ) : (
              <Card className="p-10 text-center">
                <p className="text-muted">This lesson hasn't been generated yet.</p>
                <Button onClick={() => generate(selected)} className="mt-5 px-6 py-3">
                  ✨ Generate this lesson
                </Button>
              </Card>
            )}
          </div>
        </section>

        {/* Lessons drawer (small screens) */}
        {navOpen && (
          <>
            <button
              type="button"
              aria-label="Close lessons"
              onClick={() => setNavOpen(false)}
              className="absolute inset-0 z-40 bg-black/40 backdrop-blur-sm md:hidden"
            />
            <aside className="animate-slide-in-left scrollbar-none absolute inset-y-0 left-0 z-50 flex w-72 max-w-[80%] flex-col overflow-y-auto border-r border-line bg-bg shadow-2xl md:hidden">
              {lessonsNav}
            </aside>
          </>
        )}

        {/* Ask DynoDoc — overlays the content; on lg the content reserves space so they sit side by side */}
        {chatOpen && (
          <>
            <button
              type="button"
              aria-label="Close chat"
              onClick={() => setChatOpen(false)}
              className="absolute inset-0 z-30 bg-black/40 backdrop-blur-sm lg:hidden"
            />
            <aside className="animate-slide-in-right absolute inset-y-0 right-0 z-40 flex w-full max-w-md flex-col border-l border-line bg-bg shadow-2xl lg:max-w-[24rem] lg:shadow-none">
              {chat}
            </aside>
          </>
        )}
      </div>

      {/* Select text in the lesson → "Ask DynoDoc" pill */}
      <SelectionAsk targetRef={proseRef} onAsk={askAboutSelection} />

      {/* Circular reopen button when the chat is closed */}
      {!chatOpen && (
        <button
          type="button"
          onClick={() => setChatOpen(true)}
          aria-label="Ask DynoDoc"
          className="animate-ai-glow fixed bottom-6 right-6 z-40 flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-br from-brand to-brand-2 text-white shadow-xl shadow-brand/40 transition hover:scale-105"
        >
          <ChatIcon />
        </button>
      )}
    </div>
  )
}
