import { Link } from 'react-router-dom'

import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { ProgressBar } from '@/components/ui/ProgressBar'
import { Spinner } from '@/components/ui/Spinner'
import { useAuth } from '@/features/auth/queries'
import { useCourses } from '@/features/courses/queries'

export function DashboardPage() {
  const auth = useAuth()
  const { data: courses, isPending } = useCourses()
  const firstName =
    auth.status === 'authenticated' ? (auth.user.display_name ?? auth.user.email).split(' ')[0] : ''

  return (
    <main className="px-6 py-16 sm:px-10">
      <h1 className="font-display text-3xl font-bold text-fg sm:text-4xl">
        Hey {firstName || 'there'}, what do you want to learn?
      </h1>
      <p className="mt-3 text-muted">Start a new journey, or pick up where you left off.</p>
      <Link to="/learn">
        <Button className="mt-8 px-7 py-3.5">+ Start a new course</Button>
      </Link>

      <section className="mt-16">
        <h2 className="font-display text-xl font-semibold text-fg">Your courses</h2>
        {isPending ? (
          <div className="mt-6 flex justify-center">
            <Spinner />
          </div>
        ) : courses && courses.length > 0 ? (
          <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {courses.map((course) => (
              <Link key={course.id} to={`/courses/${course.id}`}>
                <Card className="p-5 transition hover:-translate-y-1 hover:border-brand/40">
                  <p className="text-xs uppercase tracking-wider text-brand">{course.status}</p>
                  <h3 className="mt-1 font-display text-lg font-semibold text-fg">{course.title}</h3>
                  <p className="mt-1 line-clamp-2 text-sm text-muted">{course.goal}</p>
                  <div className="mt-4 flex items-center gap-3">
                    <ProgressBar value={course.completion_percent} className="flex-1" />
                    <span className="text-xs font-semibold text-fg">
                      {course.completion_percent}%
                    </span>
                  </div>
                  <p className="mt-2 text-xs text-muted">
                    {course.average_score > 0
                      ? `Avg quiz score ${course.average_score}%`
                      : 'No quizzes taken yet'}
                  </p>
                </Card>
              </Link>
            ))}
          </div>
        ) : (
          <Card className="mt-6 p-8 text-center">
            <p className="text-muted">
              No courses yet — tell us what you want to learn to create your first one.
            </p>
            <Link to="/learn">
              <Button className="mt-5 px-6 py-3">Start learning</Button>
            </Link>
          </Card>
        )}
      </section>
    </main>
  )
}
