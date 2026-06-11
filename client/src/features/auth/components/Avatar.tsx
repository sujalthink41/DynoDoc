import type { UserProfile } from '@/features/auth/types'

/** User avatar — Google photo if available, else a gradient initial. Pass `className`
 * to size it (e.g. "h-9 w-9" in nav, "h-24 w-24 text-3xl" on the profile page). */
export function Avatar({ user, className = 'h-9 w-9' }: { user: UserProfile; className?: string }) {
  const name = user.display_name ?? user.email
  if (user.avatar_url) {
    return (
      <img
        src={user.avatar_url}
        alt={name}
        referrerPolicy="no-referrer"
        className={`${className} rounded-full object-cover ring-2 ring-brand/50`}
      />
    )
  }
  return (
    <span
      className={`${className} flex items-center justify-center rounded-full bg-gradient-to-br from-brand to-brand-2 font-bold text-white ring-2 ring-brand/40`}
    >
      {name.charAt(0).toUpperCase()}
    </span>
  )
}
