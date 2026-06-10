import { Spinner } from '@/components/ui/Spinner'
import { logout } from '@/features/auth/api/auth'
import { LoginCard } from '@/features/auth/components/LoginCard'
import { ProfileCard } from '@/features/auth/components/ProfileCard'
import { useCurrentUser } from '@/features/auth/hooks/useCurrentUser'

function App() {
  const { state, reload } = useCurrentUser()

  const handleLogout = () => {
    void logout().finally(reload)
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-gradient-to-br from-indigo-50 via-white to-purple-50 px-4">
      {state.status === 'loading' && <Spinner />}
      {state.status === 'anonymous' && <LoginCard />}
      {state.status === 'authenticated' && (
        <ProfileCard user={state.user} onLogout={handleLogout} />
      )}
    </main>
  )
}

export default App
