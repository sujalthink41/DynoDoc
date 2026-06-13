import { Link, Outlet } from 'react-router-dom'

import { Avatar } from '@/features/auth/components/Avatar'
import { useAuth } from '@/features/auth/queries'
import { PlayerChips } from '@/features/game/components/PlayerChips'
import { ThemeToggle } from '@/features/theme/ThemeToggle'

/** Shell for authenticated pages: a top bar (logo, theme toggle, avatar) + content. */
export function AppLayout() {
  const auth = useAuth()

  return (
    <div className="flex h-screen flex-col">
      {/* Product-wide ambient background — soft brand aurora + faint grid. */}
      <div aria-hidden className="pointer-events-none fixed inset-0 z-0 overflow-hidden">
        <div className="animate-blob absolute -left-40 -top-40 h-[38rem] w-[38rem] rounded-full bg-brand/10 blur-3xl" />
        <div className="animate-blob animation-delay-2000 absolute top-1/3 -right-40 h-[34rem] w-[34rem] rounded-full bg-purple-500/10 blur-3xl" />
        <div className="animate-blob animation-delay-4000 absolute -bottom-40 left-1/3 h-[32rem] w-[32rem] rounded-full bg-brand-2/10 blur-3xl" />
        <div className="absolute inset-0 bg-dots text-muted/25 [mask-image:radial-gradient(ellipse_at_center,black,transparent_75%)]" />
      </div>

      <header className="relative z-40 shrink-0 border-b border-line bg-elevated backdrop-blur">
        <div className="flex items-center justify-between px-6 py-3">
          <Link to="/" className="flex items-center gap-2">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-brand to-brand-2 font-display text-base font-bold text-white">
              D
            </span>
            <span className="font-display font-semibold tracking-tight text-fg">DynoDoc</span>
          </Link>
          <div className="flex items-center gap-3">
            {auth.status === 'authenticated' && (
              <Link
                to="/games"
                className="flex items-center gap-1.5 rounded-full px-3 py-1.5 text-sm font-medium text-muted transition hover:bg-surface hover:text-fg"
              >
                🎮 <span className="hidden sm:inline">Games</span>
              </Link>
            )}
            <PlayerChips />
            <ThemeToggle />
            {auth.status === 'authenticated' && (
              <Link to="/profile" aria-label="Your profile">
                <Avatar user={auth.user} />
              </Link>
            )}
          </div>
        </div>
      </header>
      <div className="relative z-10 min-h-0 flex-1 overflow-y-auto">
        <Outlet />
      </div>
    </div>
  )
}
