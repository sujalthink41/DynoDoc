import { Link } from 'react-router-dom'

import { DynoCoin } from '@/components/ui/DynoCoin'
import { useAuth } from '@/features/auth/queries'
import { useProfile } from '@/features/game/queries'

/** Compact streak + DynoCoin chips for the top bar; links to the Daily Dash. */
export function PlayerChips() {
  const auth = useAuth()
  const { data } = useProfile(auth.status === 'authenticated')
  if (auth.status !== 'authenticated' || !data) return null

  return (
    <Link
      to="/games"
      className="flex items-center gap-2 rounded-full border border-line bg-surface px-1 py-1 pr-2.5 text-sm transition hover:border-brand/40"
      aria-label="Arcade, streak and coins"
    >
      <span
        className={`flex items-center gap-1 rounded-full px-2 py-0.5 font-semibold ${
          data.current_streak > 0 ? 'text-orange-500' : 'text-muted'
        }`}
        title="Daily streak"
      >
        🔥 {data.current_streak}
      </span>
      <span className="flex items-center gap-1.5 font-semibold text-amber-500" title="DynoCoins">
        <DynoCoin className="h-4 w-4" /> {data.coins}
      </span>
    </Link>
  )
}
