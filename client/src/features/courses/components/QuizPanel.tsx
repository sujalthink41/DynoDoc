import { useState } from 'react'
import { toast } from 'sonner'

import { AIThinking } from '@/components/ui/AIThinking'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { useAttemptQuiz, useGenerateQuiz } from '@/features/courses/queries'
import type { LessonState, QuizResult, QuizView } from '@/features/courses/types'
import { ApiError } from '@/lib/apiClient'
import { celebrate } from '@/lib/celebrate'

interface QuizPanelProps {
  lectureId: string
  lesson: LessonState
}

type Tone = 'correct' | 'wrong' | 'chosen' | 'neutral'

const TONES: Record<Tone, string> = {
  correct: 'border-green-500/60 bg-green-500/10 text-fg',
  wrong: 'border-red-500/60 bg-red-500/10 text-fg',
  chosen: 'border-brand/60 bg-brand/10 text-fg',
  neutral: 'border-line text-muted hover:border-brand/40',
}

export function QuizPanel({ lectureId, lesson }: QuizPanelProps) {
  const topicIndex = lesson.index
  const generateQuiz = useGenerateQuiz(lectureId)
  const attemptQuiz = useAttemptQuiz(lectureId)
  const [quiz, setQuiz] = useState<QuizView | null>(null)
  const [answers, setAnswers] = useState<Record<number, number>>({})
  const [result, setResult] = useState<QuizResult | null>(null)

  const reviewMode = quiz?.mastered === true && result === null

  const open = () => {
    generateQuiz.mutate(topicIndex, {
      onSuccess: (data) => {
        setQuiz(data)
        setAnswers({})
        setResult(null)
      },
      onError: () => toast.error('Could not load the quiz. Try again in a moment.'),
    })
  }

  const retake = () => {
    setAnswers({})
    setResult(null)
  }

  const submit = () => {
    if (!quiz) return
    if (Object.keys(answers).length < quiz.questions.length) {
      toast.error('Answer every question before submitting.')
      return
    }
    const ordered = quiz.questions.map((_, i) => answers[i])
    attemptQuiz.mutate(
      { topicIndex, answers: ordered },
      {
        onSuccess: (res) => {
          setResult(res)
          if (res.mastered) {
            celebrate()
            toast.success(`Perfect — 100%! Lesson mastered 🏆`)
          } else if (res.passed) {
            celebrate()
            toast.success(`Passed with ${res.score}% — next lesson unlocked! 🎉`)
          } else {
            toast.error(`Scored ${res.score}%. You need 80% — review the lesson and retry.`)
          }
        },
        onError: (error) => {
          if (error instanceof ApiError && error.code === 'quiz_mastered') {
            toast.error("You've already mastered this quiz.")
          } else {
            toast.error('Could not submit your answers. Try again.')
          }
        },
      },
    )
  }

  // ---- Entry card (quiz not open yet) -------------------------------------
  if (!quiz) {
    const cta = lesson.mastered
      ? 'Review answers'
      : lesson.passed
        ? 'Retake to reach 100%'
        : lesson.attempted
          ? 'Try the quiz again'
          : '📝 Take a quiz'
    return (
      <Card className="mt-10 p-6 text-center">
        {lesson.mastered ? (
          <>
            <p className="font-display text-lg font-semibold text-green-500">Mastered · 100% 🏆</p>
            <p className="mx-auto mt-1 max-w-md text-sm text-muted">
              You aced this lesson. Review the questions and correct answers anytime.
            </p>
          </>
        ) : (
          <>
            <h3 className="font-display text-lg font-semibold text-fg">
              {lesson.attempted ? `Best score: ${lesson.score}%` : 'Ready to test yourself?'}
            </h3>
            <p className="mx-auto mt-1 max-w-md text-sm text-muted">
              {lesson.passed
                ? 'You passed — push for a perfect 100% to master this lesson.'
                : 'Pass a quick 5-question quiz (80%+) to unlock the next lesson.'}
            </p>
          </>
        )}
        {generateQuiz.isPending ? (
          <div className="mt-5">
            <AIThinking label="Loading your quiz…" />
          </div>
        ) : (
          <Button onClick={open} variant={lesson.mastered ? 'ghost' : 'primary'} className="mt-5 px-6 py-3">
            {cta}
          </Button>
        )}
      </Card>
    )
  }

  // ---- Quiz open (interactive, graded, or mastered review) ----------------
  const locked = reviewMode || result !== null

  const toneFor = (qi: number, oi: number): Tone => {
    const chosen = answers[qi] === oi
    if (reviewMode) {
      return quiz.answers?.[qi] === oi ? 'correct' : 'neutral'
    }
    if (result) {
      const item = result.results[qi]
      if (result.mastered && item.answer_index === oi) return 'correct'
      if (chosen) return item.correct ? 'correct' : 'wrong'
      return 'neutral'
    }
    return chosen ? 'chosen' : 'neutral'
  }

  return (
    <Card className="mt-10 p-6">
      <div className="flex items-center justify-between">
        <h3 className="font-display text-lg font-semibold text-fg">
          {reviewMode ? 'Quiz review' : 'Lesson quiz'}
        </h3>
        {reviewMode && (
          <span className="rounded-full bg-green-500/15 px-3 py-1 text-xs font-semibold text-green-500">
            100% 🏆
          </span>
        )}
      </div>
      <p className="mt-1 text-sm text-muted">
        {reviewMode
          ? 'You mastered this lesson — here are the correct answers.'
          : 'Choose the best answer for each question.'}
      </p>

      <ol className="mt-6 space-y-6">
        {quiz.questions.map((q, qi) => (
          <li key={qi}>
            <p className="font-medium text-fg">
              {qi + 1}. {q.question}
            </p>
            <div className="mt-3 space-y-2">
              {q.options.map((option, oi) => (
                <button
                  key={oi}
                  type="button"
                  disabled={locked}
                  onClick={() => setAnswers((prev) => ({ ...prev, [qi]: oi }))}
                  className={`flex w-full items-center gap-3 rounded-xl border px-4 py-2.5 text-left text-sm transition disabled:cursor-default ${TONES[toneFor(qi, oi)]}`}
                >
                  <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-[11px] font-bold ring-1 ring-current">
                    {String.fromCharCode(65 + oi)}
                  </span>
                  <span>{option}</span>
                </button>
              ))}
            </div>
          </li>
        ))}
      </ol>

      {reviewMode ? (
        <div className="mt-6 border-t border-line pt-6 text-center">
          <Button variant="ghost" onClick={() => setQuiz(null)} className="px-5 py-2.5">
            Close review
          </Button>
        </div>
      ) : result ? (
        <div className="mt-6 flex flex-col items-center gap-3 border-t border-line pt-6 text-center">
          <p
            className={`font-display text-2xl font-bold ${
              result.mastered ? 'text-green-500' : 'text-fg'
            }`}
          >
            {result.correct_count}/{result.total} correct · {result.score}%
          </p>
          <p className="text-sm text-muted">
            {result.mastered
              ? 'Lesson mastered — perfect score! 🏆'
              : result.passed
                ? 'Passed! The next lesson is unlocked — retake to reach 100%.'
                : 'You need 80% to move on. Review the lesson and try again.'}
          </p>
          {result.can_retake && (
            <Button variant="ghost" onClick={retake} className="px-5 py-2.5">
              {result.passed ? 'Retake for 100%' : 'Try again'}
            </Button>
          )}
        </div>
      ) : (
        <div className="mt-6 border-t border-line pt-6 text-center">
          <Button onClick={submit} disabled={attemptQuiz.isPending} className="px-7 py-3">
            {attemptQuiz.isPending ? 'Grading…' : 'Submit answers'}
          </Button>
        </div>
      )}
    </Card>
  )
}
