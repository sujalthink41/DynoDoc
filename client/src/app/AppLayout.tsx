import { useEffect, useRef } from 'react'
import { Link, NavLink, Outlet, useLocation } from 'react-router-dom'
import { toast } from 'sonner'

import { Avatar } from '@/features/auth/components/Avatar'
import { useAuth } from '@/features/auth/queries'
import { PlayerChips } from '@/features/game/components/PlayerChips'
import { useClaimVisit, useProfile } from '@/features/game/queries'
import { ThemeToggle } from '@/features/theme/ThemeToggle'

function NavItem({
  to,
  label,
  dot,
}: {
  to: string
  label: string
  dot?: boolean
}) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `relative rounded-full px-3.5 py-1.5 text-sm font-medium transition ${
          isActive ? 'bg-brand/10 text-brand' : 'text-muted hover:bg-surface hover:text-fg'
        }`
      }
    >
      {label}
      {dot && (
        <span className="absolute -right-0.5 -top-0.5 flex h-2.5 w-2.5">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-brand opacity-75" />
          <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-brand" />
        </span>
      )}
    </NavLink>
  )
}

/** Shell for authenticated pages: a top bar (logo, nav, theme, avatar) + content. */
export function AppLayout() {
  const auth = useAuth()
  const authed = auth.status === 'authenticated'
  const { data: player } = useProfile(authed)
  const showGameDot = Boolean(player && !player.played_today)

  // Full-bleed pages own their own layout (the lesson workspace + the 3-pane
  // learn chat). Everything else shares one consistent page width.
  const { pathname } = useLocation()
  // The lesson workspace, the 3-pane learn chat, and the Arcade (its ambient
  // backdrop spans edge-to-edge) own their own layout; everything else shares
  // one consistent page width.
  const fullBleed =
    pathname.startsWith('/lectures/') || pathname === '/learn' || pathname === '/games'

  // Award the once-a-day visit bonus on the first app load of the day.
  const claimVisit = useClaimVisit()
  const claimedRef = useRef(false)
  useEffect(() => {
    if (!authed || claimedRef.current) return
    claimedRef.current = true
    claimVisit.mutate(undefined, {
      onSuccess: (bonus) => {
        if (bonus.awarded > 0) toast.success(`+${bonus.awarded} DynoCoins for showing up today! 🪙`)
      },
    })
  }, [authed, claimVisit])

  return (
    <div className="flex h-screen flex-col">
      {/* Product-wide ambient background — soft brand aurora + faint grid. */}
      <div aria-hidden className="pointer-events-none fixed inset-0 z-0 overflow-hidden">
        <div className="animate-blob absolute -left-40 -top-40 h-[38rem] w-[38rem] rounded-full bg-brand/5 blur-3xl" />
        <div className="animate-blob animation-delay-2000 absolute top-1/3 -right-40 h-[34rem] w-[34rem] rounded-full bg-purple-500/5 blur-3xl" />
        <div className="animate-blob animation-delay-4000 absolute -bottom-40 left-1/3 h-[32rem] w-[32rem] rounded-full bg-brand-2/5 blur-3xl" />
        <div className="absolute inset-0 bg-dots text-muted/25 [mask-image:radial-gradient(ellipse_at_center,black,transparent_75%)]" />
      </div>

      <header className="relative z-40 shrink-0 border-b border-line/50 bg-elevated/60 backdrop-blur-2xl backdrop-saturate-150">
        <div className="mx-auto flex w-full max-w-7xl items-center justify-between gap-4 px-6 py-2.5 sm:px-10">
          <div className="flex items-center gap-5">
            <Link to="/" className="flex items-center gap-2">
              <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-br from-brand to-brand-2 font-display text-base font-bold text-white shadow-sm shadow-brand/30">
                D
              </span>
              <span className="font-display font-semibold tracking-tight text-fg">DynoDoc</span>
            </Link>
            {authed && (
              <nav className="hidden items-center gap-1 sm:flex">
                <NavItem to="/app" label="Learn" />
                <NavItem to="/games" label="Arcade" dot={showGameDot} />
              </nav>
            )}
          </div>

          <div className="flex items-center gap-3">
            {authed && (
              <Link
                to="/pricing"
                className="hidden items-center gap-1 rounded-full bg-gradient-to-r from-brand to-brand-2 px-3.5 py-1.5 text-sm font-semibold text-white shadow-sm shadow-brand/30 transition hover:opacity-90 sm:inline-flex"
              >
                ✨ Upgrade
              </Link>
            )}
            <PlayerChips />
            <ThemeToggle />
            {authed && (
              <Link to="/profile" aria-label="Your profile">
                <Avatar user={auth.user} />
              </Link>
            )}
          </div>
        </div>
      </header>

      <div className="relative z-10 min-h-0 flex-1 overflow-y-auto">
        {fullBleed ? (
          <Outlet />
        ) : (
          <div className="mx-auto w-full max-w-7xl px-6 py-10 sm:px-10">
            <Outlet />
          </div>
        )}
      </div>
    </div>
  )
}
