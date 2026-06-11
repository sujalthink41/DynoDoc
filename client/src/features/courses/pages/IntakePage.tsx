import { useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { AIThinking } from '@/components/ui/AIThinking'
import { Button } from '@/components/ui/Button'
import { useAnswerIntake, useCreateCourse, useStartIntake } from '@/features/courses/queries'
import type { IntakeSession } from '@/features/courses/types'

interface ChatMessage {
  id: number
  role: 'user' | 'ai'
  text: string
}

export function IntakePage() {
  const navigate = useNavigate()
  const idRef = useRef(0)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [intakeId, setIntakeId] = useState<string | null>(null)
  const [ready, setReady] = useState(false)

  const startIntake = useStartIntake()
  const answerIntake = useAnswerIntake()
  const createCourse = useCreateCourse()
  const busy = startIntake.isPending || answerIntake.isPending || createCourse.isPending

  const addMessage = (role: ChatMessage['role'], text: string) => {
    idRef.current += 1
    setMessages((prev) => [...prev, { id: idRef.current, role, text }])
  }

  const applySession = (session: IntakeSession) => {
    setIntakeId(session.id)
    if (session.status === 'ready') {
      setReady(true)
      addMessage('ai', "Perfect — I've got everything I need. Ready to build your course! 🚀")
    } else {
      addMessage('ai', session.questions.join('\n'))
    }
  }

  const handleSend = () => {
    const text = input.trim()
    if (!text || busy || ready) return
    setInput('')
    addMessage('user', text)
    if (!intakeId) {
      startIntake.mutate(text, { onSuccess: applySession })
    } else {
      answerIntake.mutate({ id: intakeId, answer: text }, { onSuccess: applySession })
    }
  }

  const handleBuild = () => {
    if (!intakeId) return
    createCourse.mutate(intakeId, { onSuccess: (course) => navigate(`/courses/${course.id}`) })
  }

  const started = messages.length > 0

  return (
    <main className="mx-auto flex min-h-[calc(100vh-57px)] max-w-2xl flex-col px-6 py-10">
      {!started ? (
        <div className="flex flex-1 flex-col items-center justify-center text-center">
          <h1 className="font-display text-3xl font-bold text-fg sm:text-4xl">
            What do you want to learn?
          </h1>
          <p className="mt-3 text-muted">
            Tell me your goal — I'll ask a couple of questions, then build your course.
          </p>
        </div>
      ) : (
        <div className="flex-1 space-y-4 pb-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={message.role === 'user' ? 'flex justify-end' : 'flex justify-start'}
            >
              <div
                className={
                  message.role === 'user'
                    ? 'max-w-[80%] whitespace-pre-line rounded-2xl rounded-br-sm bg-gradient-to-r from-brand to-brand-2 px-4 py-2.5 text-white'
                    : 'max-w-[85%] whitespace-pre-line rounded-2xl rounded-bl-sm border border-line bg-surface px-4 py-2.5 text-fg'
                }
              >
                {message.text}
              </div>
            </div>
          ))}
          {busy && <AIThinking label="DynoDoc is thinking…" />}
          {ready && (
            <Button onClick={handleBuild} disabled={busy} className="mt-2 w-full px-6 py-3.5">
              {createCourse.isPending ? 'Building your course…' : '✨ Build my course'}
            </Button>
          )}
        </div>
      )}

      {!ready && (
        <form
          onSubmit={(e) => {
            e.preventDefault()
            handleSend()
          }}
          className="sticky bottom-6 mt-4 flex items-center gap-2 rounded-2xl border border-line bg-elevated p-2 shadow-xl backdrop-blur"
        >
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={started ? 'Type your answer…' : 'e.g. I want to learn Python'}
            disabled={busy}
            className="flex-1 bg-transparent px-3 py-2 text-fg placeholder:text-muted focus:outline-none"
          />
          <Button type="submit" disabled={busy || !input.trim()} className="px-5 py-2.5">
            Send
          </Button>
        </form>
      )}
    </main>
  )
}
