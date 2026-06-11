import type { ReactNode } from 'react'
import { useNavigate } from 'react-router-dom'

import { Button } from '@/components/ui/Button'
import { loginWithGoogle } from '@/features/auth/api/auth'
import { useAuth } from '@/features/auth/queries'

/** Landing CTA: signed-in users go to the dashboard, others start Google login. */
export function StartLearningButton({
  className,
  children,
}: {
  className?: string
  children: ReactNode
}) {
  const auth = useAuth()
  const navigate = useNavigate()

  const handleClick = () => {
    if (auth.status === 'authenticated') {
      navigate('/app')
    } else {
      loginWithGoogle()
    }
  }

  return (
    <Button onClick={handleClick} className={className}>
      {children}
    </Button>
  )
}
