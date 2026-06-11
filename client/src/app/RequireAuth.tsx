import { Outlet } from 'react-router-dom'

import { Spinner } from '@/components/ui/Spinner'
import { SignInGate } from '@/features/auth/components/SignInGate'
import { useAuth } from '@/features/auth/queries'

/** Route guard for the actual product: blocks anonymous users with a sign-in gate. */
export function RequireAuth() {
  const auth = useAuth()

  if (auth.status === 'loading') {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Spinner />
      </div>
    )
  }
  if (auth.status === 'anonymous') {
    return <SignInGate />
  }
  return <Outlet />
}
