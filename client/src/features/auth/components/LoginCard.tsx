import { GoogleButton } from '@/features/auth/components/GoogleButton'
import { loginWithGoogle } from '@/features/auth/api/auth'

export function LoginCard() {
  return (
    <div className="w-full max-w-md rounded-3xl bg-white/80 p-8 text-center shadow-2xl ring-1 ring-slate-900/5 backdrop-blur-xl sm:p-10">
      {/* Brand mark */}
      <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 text-2xl font-bold text-white shadow-lg">
        D
      </div>

      <h1 className="bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-3xl font-bold tracking-tight text-transparent">
        Welcome to DynoDoc
      </h1>
      <p className="mt-3 text-sm leading-relaxed text-slate-500">
        Your AI-powered learning journey starts here. Sign in to build your
        personalized roadmap.
      </p>

      <div className="mt-8">
        <GoogleButton onClick={loginWithGoogle} />
      </div>

      <p className="mt-6 text-xs text-slate-400">
        By continuing you agree to our Terms &amp; Privacy Policy.
      </p>
    </div>
  )
}
