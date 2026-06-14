import { Link } from 'react-router-dom'

import { Card } from '@/components/ui/Card'
import { ProgressBar } from '@/components/ui/ProgressBar'
import { Spinner } from '@/components/ui/Spinner'
import { useAuth } from '@/features/auth/queries'
import { useCourses } from '@/features/courses/queries'
import { useProfile } from '@/features/game/queries'

export function DashboardPage() {
  const auth = useAuth()
  const { data: courses, isPending } = useCourses()
  const { data: player } = useProfile(auth.status === 'authenticated')
  const firstName =
    auth.status === 'authenticated' ? (auth.user.display_name ?? auth.user.email).split(' ')[0] : ''
  const nudgeToday = player && !player.played_today

  return (
    <main className="mx-auto max-w-7xl px-6 py-12 sm:px-10">
      {/* Daily game nudge — keep the streak alive */}
      {nudgeToday && (
        <Link to="/games/connections" className="mb-8 block">
          <div className="card-sheen flex items-center justify-between gap-4 rounded-2xl border border-brand/30 bg-gradient-to-r from-brand/10 to-brand-2/10 px-5 py-4 transition hover:-translate-y-0.5 hover:border-brand/50">
            <div className="flex items-center gap-3">
              <span className="text-2xl">🔥</span>
              <p className="text-sm font-medium text-fg">
                {player.current_streak > 0
                  ? `Keep your ${player.current_streak}-day streak alive — play today's game!`
                  : "Play today's game to start a streak and earn DynoCoins!"}
              </p>
            </div>
            <span className="hidden shrink-0 rounded-full bg-gradient-to-r from-brand to-brand-2 px-4 py-2 text-sm font-semibold text-white sm:inline">
              Play now →
            </span>
          </div>
        </Link>
      )}

      {/* Hero */}
      <p className="text-sm font-medium uppercase tracking-wider text-brand">Welcome back</p>
      <h1 className="mt-2 font-display text-4xl font-bold tracking-tight text-fg sm:text-5xl">
        Hey {firstName || 'there'}, what will you{' '}
        <span className="bg-gradient-to-r from-brand to-brand-2 bg-clip-text text-transparent">
          master
        </span>{' '}
        today?
      </h1>
      <p className="mt-3 max-w-lg text-muted">
        Pick up where you left off, or start a brand-new learning journey.
      </p>

      {/* Start a new course CTA */}
      <Link to="/learn" className="mt-8 block sm:inline-block">
        <div className="card-sheen group flex items-center gap-4 rounded-2xl border border-brand/40 bg-gradient-to-r from-brand to-brand-2 px-6 py-4 shadow-lg shadow-brand/30 transition hover:-translate-y-0.5">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/20 text-xl font-bold text-white">
            +
          </span>
          <div>
            <p className="font-display text-lg font-semibold text-white">Start a new course</p>
            <p className="text-sm text-white/80">Tell DynoDoc your goal — get a custom roadmap.</p>
          </div>
        </div>
      </Link>

      {/* Courses */}
      <section className="mt-14">
        <h2 className="font-display text-xl font-semibold text-fg">Your courses</h2>
        {isPending ? (
          <div className="mt-6 flex justify-center">
            <Spinner />
          </div>
        ) : courses && courses.length > 0 ? (
          <div className="mt-6 grid gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {courses.map((course) => (
              <Link key={course.id} to={`/courses/${course.id}`} className="group">
                <Card className="relative h-full overflow-hidden p-5 transition duration-300 hover:-translate-y-1.5 hover:border-brand/50 hover:shadow-2xl hover:shadow-brand/10">
                  <span className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-brand to-brand-2 opacity-0 transition group-hover:opacity-100" />
                  <div className="flex items-center justify-between">
                    <span className="rounded-full bg-brand/10 px-2.5 py-1 text-[0.65rem] font-bold uppercase tracking-wide text-brand">
                      {course.status}
                    </span>
                    <span className="font-display text-sm font-bold text-fg">
                      {course.completion_percent}%
                    </span>
                  </div>
                  <h3 className="mt-3 font-display text-lg font-semibold leading-snug text-fg">
                    {course.title}
                  </h3>
                  <p className="mt-1 line-clamp-2 text-sm text-muted">{course.goal}</p>
                  <div className="mt-4">
                    <ProgressBar value={course.completion_percent} />
                  </div>
                  <p className="mt-3 text-xs text-muted">
                    {course.average_score > 0
                      ? `Avg quiz score ${course.average_score}%`
                      : 'No quizzes taken yet'}
                  </p>
                </Card>
              </Link>
            ))}
          </div>
        ) : (
          <Card className="mt-6 p-10 text-center">
            <span className="text-4xl">🚀</span>
            <p className="mt-3 text-muted">
              No courses yet — tell us what you want to learn to create your first one.
            </p>
            <Link to="/learn">
              <span className="mt-5 inline-block rounded-full bg-gradient-to-r from-brand to-brand-2 px-6 py-3 text-sm font-semibold text-white">
                Start learning →
              </span>
            </Link>
          </Card>
        )}
      </section>
    </main>
  )
}
