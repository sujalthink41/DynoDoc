import { Link, Outlet } from 'react-router-dom'

import { Avatar } from '@/features/auth/components/Avatar'
import { useAuth } from '@/features/auth/queries'
import { ThemeToggle } from '@/features/theme/ThemeToggle'

/** Shell for authenticated pages: a top bar (logo, theme toggle, avatar) + content. */
export function AppLayout() {
  const auth = useAuth()

  return (
    <div className="flex h-screen flex-col">
      <header className="z-40 shrink-0 border-b border-line bg-elevated backdrop-blur">
        <div className="flex items-center justify-between px-6 py-3">
          <Link to="/" className="flex items-center gap-2">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-brand to-brand-2 font-display text-base font-bold text-white">
              D
            </span>
            <span className="font-display font-semibold tracking-tight text-fg">DynoDoc</span>
          </Link>
          <div className="flex items-center gap-3">
            <ThemeToggle />
            {auth.status === 'authenticated' && (
              <Link to="/profile" aria-label="Your profile">
                <Avatar user={auth.user} />
              </Link>
            )}
          </div>
        </div>
      </header>
      <div className="min-h-0 flex-1 overflow-y-auto">
        <Outlet />
      </div>
    </div>
  )
}
