import { useNavigate } from 'react-router-dom'

import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Avatar } from '@/features/auth/components/Avatar'
import { useAuth, useLogout } from '@/features/auth/queries'

export function ProfilePage() {
  const auth = useAuth()
  const logoutMutation = useLogout()
  const navigate = useNavigate()

  // RequireAuth guarantees we're authenticated; this also narrows the type.
  if (auth.status !== 'authenticated') return null
  const { user } = auth

  const handleLogout = () => {
    logoutMutation.mutate(undefined, { onSuccess: () => navigate('/') })
  }

  return (
    <main className="mx-auto max-w-2xl px-6 py-16">
      <Card className="p-8 text-center">
        <div className="flex flex-col items-center">
          <Avatar user={user} className="h-24 w-24 text-3xl" />
          <h1 className="mt-5 font-display text-2xl font-bold text-fg">
            {user.display_name ?? user.email}
          </h1>
          <p className="mt-1 text-muted">{user.email}</p>
        </div>

        {/* Learning stats and "my courses" will live here as we build them. */}

        <Button
          onClick={handleLogout}
          disabled={logoutMutation.isPending}
          className="mt-10 w-full px-4 py-3"
        >
          {logoutMutation.isPending ? 'Logging out…' : 'Log out'}
        </Button>
      </Card>
    </main>
  )
}
