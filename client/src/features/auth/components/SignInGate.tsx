import { Card } from '@/components/ui/Card'
import { loginWithGoogle } from '@/features/auth/api/auth'
import { GoogleButton } from '@/features/auth/components/GoogleButton'

/** Shown when an unauthenticated user hits a protected page: "sign in first". */
export function SignInGate() {
  return (
    <main className="flex min-h-screen items-center justify-center px-4">
      <Card className="w-full max-w-md p-10 text-center">
        <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-brand to-brand-2 font-display text-2xl font-bold text-white shadow-lg shadow-brand/30">
          D
        </div>
        <h1 className="font-display text-2xl font-bold text-fg">Sign in to continue</h1>
        <p className="mt-2 text-muted">
          Sign in first, then enjoy your personalized learning journey.
        </p>
        <div className="mt-8">
          <GoogleButton onClick={loginWithGoogle} />
        </div>
      </Card>
    </main>
  )
}
