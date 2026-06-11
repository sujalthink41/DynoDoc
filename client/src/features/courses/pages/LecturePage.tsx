import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { useParams } from 'react-router-dom'
import remarkGfm from 'remark-gfm'

import { AIThinking } from '@/components/ui/AIThinking'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Spinner } from '@/components/ui/Spinner'
import {
  useGenerateReferences,
  useGenerateTopic,
  useLecture,
} from '@/features/courses/queries'
import type { DocView, ReferenceView } from '@/features/courses/types'

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

export function LecturePage() {
  const { lectureId = '' } = useParams()
  const { data: lecture, isPending } = useLecture(lectureId)
  const generateTopic = useGenerateTopic(lectureId)
  const generateReferences = useGenerateReferences(lectureId)
  const [selected, setSelected] = useState<number | null>(null)

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

  const selectTopic = (index: number) => {
    setSelected(index)
    if (!docFor(index) && generateTopic.variables !== index) {
      generateTopic.mutate(index)
    }
  }

  const selectedDoc = selected !== null ? docFor(selected) : undefined

  return (
    <main className="mx-auto max-w-5xl px-6 py-10">
      <p className="text-xs uppercase tracking-wider text-brand">Lecture {lecture.position}</p>
      <h1 className="mt-1 font-display text-3xl font-bold text-fg">{lecture.title}</h1>
      <p className="mt-2 text-muted">{lecture.summary}</p>

      <div className="mt-8 grid gap-8 md:grid-cols-[16rem_1fr]">
        {/* Sidebar: topic list */}
        <aside className="md:sticky md:top-20 md:self-start">
          <p className="text-xs font-semibold uppercase tracking-wider text-muted">Topics</p>
          <nav className="mt-3 space-y-1">
            {lecture.topics.map((topic, i) => {
              const done = Boolean(docFor(i))
              const active = selected === i
              return (
                <button
                  key={topic}
                  type="button"
                  onClick={() => selectTopic(i)}
                  className={`flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm transition ${
                    active ? 'bg-brand/10 text-brand' : 'text-muted hover:bg-surface hover:text-fg'
                  }`}
                >
                  <span
                    className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-[10px] font-bold ${
                      done ? 'bg-brand text-white' : 'ring-1 ring-line'
                    }`}
                  >
                    {done ? '✓' : i + 1}
                  </span>
                  <span className="line-clamp-2">{topic}</span>
                </button>
              )
            })}
          </nav>
        </aside>

        {/* Main: selected topic's lesson */}
        <section>
          {selected === null ? (
            <Card className="p-10 text-center text-muted">
              Pick a topic on the left to start learning.
            </Card>
          ) : generatingIndex === selected ? (
            <AIThinking label="Writing this lesson… a few seconds" />
          ) : selectedDoc ? (
            <div className="prose prose-slate max-w-none dark:prose-invert prose-headings:font-display prose-a:text-brand">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{selectedDoc.content}</ReactMarkdown>
            </div>
          ) : (
            <Card className="p-10 text-center">
              <p className="text-muted">This topic hasn't been generated yet.</p>
              <Button onClick={() => generateTopic.mutate(selected)} className="mt-5 px-6 py-3">
                ✨ Generate this lesson
              </Button>
            </Card>
          )}
        </section>
      </div>

      {/* Lecture-level resources */}
      <section className="mt-14 border-t border-line pt-10">
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
          <div className="mt-4">
            <Button
              variant="ghost"
              onClick={() => generateReferences.mutate()}
              className="px-5 py-2.5"
            >
              🔎 Find resources for this lecture
            </Button>
          </div>
        )}
      </section>
    </main>
  )
}
