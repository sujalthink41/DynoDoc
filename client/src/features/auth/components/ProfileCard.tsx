import type { UserProfile } from '@/features/auth/types'

interface ProfileCardProps {
  user: UserProfile
  onLogout: () => void
}

export function ProfileCard({ user, onLogout }: ProfileCardProps) {
  const name = user.display_name ?? user.email

  return (
    <div className="w-full max-w-md rounded-3xl bg-white/80 p-8 text-center shadow-2xl ring-1 ring-slate-900/5 backdrop-blur-xl sm:p-10">
      {user.avatar_url ? (
        <img
          src={user.avatar_url}
          alt={name}
          className="mx-auto h-20 w-20 rounded-full shadow-lg ring-2 ring-white"
        />
      ) : (
        <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 text-2xl font-bold text-white">
          {name.charAt(0).toUpperCase()}
        </div>
      )}

      <h1 className="mt-5 text-2xl font-bold text-slate-800">
        You&apos;re signed in 🎉
      </h1>
      <p className="mt-1 text-slate-600">{name}</p>
      <p className="text-sm text-slate-400">{user.email}</p>

      <button
        type="button"
        onClick={onLogout}
        className="mt-8 w-full rounded-xl bg-slate-800 px-4 py-3 font-medium text-white transition hover:bg-slate-900 focus:outline-none focus-visible:ring-2 focus-visible:ring-slate-500 focus-visible:ring-offset-2"
      >
        Sign out
      </button>
    </div>
  )
}
