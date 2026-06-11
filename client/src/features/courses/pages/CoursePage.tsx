import { Link, useParams } from 'react-router-dom'

import { Card } from '@/components/ui/Card'
import { Spinner } from '@/components/ui/Spinner'
import { useCourse } from '@/features/courses/queries'

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
    <main className="mx-auto max-w-3xl px-6 py-12">
      <p className="text-xs uppercase tracking-wider text-brand">Your roadmap</p>
      <h1 className="mt-1 font-display text-3xl font-bold text-fg sm:text-4xl">{course.title}</h1>
      <p className="mt-2 text-muted">{course.goal}</p>

      <div className="mt-12">
        {course.lectures.map((lecture, i) => (
          <div key={lecture.id} className="flex gap-4">
            <div className="flex flex-col items-center">
              <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-brand to-brand-2 text-sm font-bold text-white">
                {lecture.position}
              </span>
              {i < course.lectures.length - 1 && <span className="my-1 w-px flex-1 bg-line" />}
            </div>
            <Link to={`/lectures/${lecture.id}`} className="mb-6 block flex-1">
              <Card className="p-5 transition hover:-translate-y-0.5 hover:border-brand/40">
                <h3 className="font-display text-lg font-semibold text-fg">{lecture.title}</h3>
                <p className="mt-1 text-sm text-muted">{lecture.summary}</p>
                <div className="mt-3 flex flex-wrap gap-2">
                  {lecture.topics.map((topic) => (
                    <span
                      key={topic}
                      className="rounded-full bg-brand/10 px-2.5 py-1 text-xs font-medium text-brand"
                    >
                      {topic}
                    </span>
                  ))}
                </div>
              </Card>
            </Link>
          </div>
        ))}
      </div>
    </main>
  )
}
