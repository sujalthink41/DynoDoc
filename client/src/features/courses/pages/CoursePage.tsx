import { Link, useParams } from 'react-router-dom'

import { Breadcrumb, HomeIcon } from '@/components/ui/Breadcrumb'
import { Card } from '@/components/ui/Card'
import { ProgressBar } from '@/components/ui/ProgressBar'
import { Spinner } from '@/components/ui/Spinner'
import { useCourse } from '@/features/courses/queries'
import type { LectureSummary } from '@/features/courses/types'

type ModuleStatus = 'done' | 'active' | 'todo'

function moduleStatus(lecture: LectureSummary): ModuleStatus {
  if (lecture.lessons_total > 0 && lecture.lessons_passed >= lecture.lessons_total) return 'done'
  if (lecture.lessons_passed > 0) return 'active'
  return 'todo'
}

const STATUS_PILL: Record<ModuleStatus, { label: string; className: string }> = {
  done: { label: 'Completed', className: 'bg-green-500/15 text-green-500' },
  active: { label: 'In progress', className: 'bg-brand/15 text-brand' },
  todo: { label: 'Not started', className: 'bg-surface text-muted' },
}

export function CoursePage() {
  const { courseId = '' } = useParams()
  const { data: course, isPending, isError } = useCourse(courseId)

  if (isPending) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <Spinner />
      </div>
    )
  }
  if (isError || !course) {
    return <p className="mx-auto max-w-3xl px-6 py-16 text-muted">Course not found.</p>
  }

  return (
    <main className="mx-auto max-w-3xl px-6 py-10">
      <Breadcrumb
        items={[
          { label: 'Home', to: '/app', icon: <HomeIcon /> },
          { label: course.title },
        ]}
      />

      <p className="mt-6 text-xs uppercase tracking-wider text-brand">Your roadmap</p>
      <h1 className="mt-1 font-display text-3xl font-bold text-fg sm:text-4xl">{course.title}</h1>
      <p className="mt-2 text-muted">{course.goal}</p>

      {/* Progress summary */}
      <Card className="mt-6 flex flex-col gap-4 p-6 sm:flex-row sm:items-center sm:gap-10">
        <div className="flex-1">
          <div className="flex items-center justify-between text-sm">
            <span className="font-medium text-fg">Course progress</span>
            <span className="font-semibold text-brand">{course.completion_percent}%</span>
          </div>
          <ProgressBar value={course.completion_percent} className="mt-2" />
        </div>
        <div className="flex gap-8 sm:gap-10">
          <div className="text-center">
            <p className="font-display text-2xl font-bold text-fg">{course.lectures.length}</p>
            <p className="text-xs text-muted">Modules</p>
          </div>
          <div className="text-center">
            <p className="font-display text-2xl font-bold text-fg">
              {course.average_score > 0 ? `${course.average_score}%` : '—'}
            </p>
            <p className="text-xs text-muted">Avg quiz score</p>
          </div>
        </div>
      </Card>

      {/* Roadmap timeline */}
      <ol className="relative mt-12">
        {course.lectures.map((lecture, i) => {
          const status = moduleStatus(lecture)
          const pill = STATUS_PILL[status]
          const isLast = i === course.lectures.length - 1
          const pct =
            lecture.lessons_total > 0
              ? Math.round((lecture.lessons_passed / lecture.lessons_total) * 100)
              : 0
          return (
            <li key={lecture.id} className="relative flex gap-5 pb-8">
              {/* Node + connector */}
              <div className="flex flex-col items-center">
                <span
                  className={`relative z-10 flex h-11 w-11 shrink-0 items-center justify-center rounded-full text-sm font-bold shadow-lg transition ${
                    status === 'done'
                      ? 'bg-gradient-to-br from-green-500 to-emerald-600 text-white shadow-green-500/30'
                      : status === 'active'
                        ? 'bg-gradient-to-br from-brand to-brand-2 text-white shadow-brand/40'
                        : 'border border-line bg-elevated text-muted'
                  }`}
                >
                  {status === 'done' ? '✓' : lecture.position}
                </span>
                {!isLast && (
                  <span
                    className={`-mb-8 mt-1 w-0.5 flex-1 rounded-full ${
                      status === 'done'
                        ? 'bg-gradient-to-b from-green-500 to-brand/40'
                        : 'bg-line'
                    }`}
                  />
                )}
              </div>

              {/* Module card */}
              <Link to={`/lectures/${lecture.id}`} className="block flex-1">
                <Card className="group p-5 transition hover:-translate-y-0.5 hover:border-brand/50 hover:shadow-brand/10">
                  <div className="flex items-start justify-between gap-3">
                    <h3 className="font-display text-lg font-semibold text-fg">{lecture.title}</h3>
                    <span
                      className={`shrink-0 rounded-full px-2.5 py-1 text-xs font-semibold ${pill.className}`}
                    >
                      {pill.label}
                    </span>
                  </div>
                  <p className="mt-1 line-clamp-2 text-sm text-muted">{lecture.summary}</p>

                  <div className="mt-4 flex items-center gap-3">
                    <ProgressBar value={pct} className="flex-1" />
                    <span className="shrink-0 text-xs font-medium text-muted">
                      {lecture.lessons_passed}/{lecture.lessons_total} lessons
                    </span>
                  </div>

                  <div className="mt-4 flex items-center justify-between gap-3">
                    <div className="flex flex-wrap gap-1.5">
                      {lecture.topics.slice(0, 3).map((topic) => (
                        <span
                          key={topic}
                          className="rounded-full bg-brand/10 px-2.5 py-1 text-xs font-medium text-brand"
                        >
                          {topic}
                        </span>
                      ))}
                      {lecture.topics.length > 3 && (
                        <span className="rounded-full bg-surface px-2.5 py-1 text-xs font-medium text-muted">
                          +{lecture.topics.length - 3} more
                        </span>
                      )}
                    </div>
                    <span className="shrink-0 text-sm font-semibold text-brand opacity-0 transition group-hover:opacity-100">
                      {status === 'done' ? 'Review' : status === 'active' ? 'Continue' : 'Start'} →
                    </span>
                  </div>
                </Card>
              </Link>
            </li>
          )
        })}
      </ol>
    </main>
  )
}
