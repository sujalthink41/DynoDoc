import { useParams } from 'react-router-dom'

import { Breadcrumb, HomeIcon } from '@/components/ui/Breadcrumb'
import { Card } from '@/components/ui/Card'
import { ProgressBar } from '@/components/ui/ProgressBar'
import { Spinner } from '@/components/ui/Spinner'
import { LearningPath } from '@/features/courses/components/LearningPath'
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
    return <p className="px-6 py-16 text-center text-muted">Course not found.</p>
  }

  const total = course.lectures.length
  const completedModules = course.lectures.filter(
    (l) => l.lessons_total > 0 && l.lessons_passed >= l.lessons_total,
  ).length
  const currentLevel = Math.min(completedModules + 1, total)

  return (
    <main className="px-6 py-8 sm:px-10">
      <Breadcrumb
        items={[
          { label: 'Home', to: '/app', icon: <HomeIcon /> },
          { label: course.title },
        ]}
      />

      <div className="mt-6 flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-xs uppercase tracking-wider text-brand">Your learning path</p>
          <h1 className="mt-1 font-display text-3xl font-bold text-fg sm:text-4xl">
            {course.title}
          </h1>
          <p className="mt-2 max-w-2xl text-muted">{course.goal}</p>
        </div>

        {/* Progress / level summary */}
        <Card className="flex items-center gap-6 p-5">
          <div className="text-center">
            <p className="font-display text-2xl font-bold text-brand">
              {currentLevel}
              <span className="text-base font-medium text-muted">/{total}</span>
            </p>
            <p className="text-xs text-muted">Level</p>
          </div>
          <div className="h-10 w-px bg-line" />
          <div className="min-w-[8rem]">
            <div className="flex items-center justify-between text-xs">
              <span className="font-medium text-fg">{course.completion_percent}% complete</span>
            </div>
            <ProgressBar value={course.completion_percent} className="mt-1.5" />
            <p className="mt-1.5 text-xs text-muted">
              {course.average_score > 0 ? `Avg quiz ${course.average_score}%` : 'No quizzes yet'}
            </p>
          </div>
        </Card>
      </div>

      {/* Game-style level trail */}
      <div className="mt-8 pb-16">
        <LearningPath lectures={course.lectures} />
      </div>
    </main>
  )
}
