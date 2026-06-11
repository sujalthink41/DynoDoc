import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'

import { Button } from '@/components/ui/Button'
import { loginWithGoogle } from '@/features/auth/api/auth'
import { Avatar } from '@/features/auth/components/Avatar'
import { useAuth } from '@/features/auth/queries'
import { ThemeToggle } from '@/features/theme/ThemeToggle'

export function Navbar() {
  const auth = useAuth()

  return (
    <motion.header
      initial={{ y: -24, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: 'easeOut' }}
      className="fixed inset-x-0 top-0 z-50"
    >
      <nav className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link to="/" className="flex items-center gap-2">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-brand to-brand-2 font-display text-lg font-bold text-white shadow-lg shadow-brand/30">
            D
          </span>
          <span className="font-display text-lg font-semibold tracking-tight text-fg">DynoDoc</span>
        </Link>

        <div className="hidden items-center gap-8 text-sm text-muted md:flex">
          <a href="#how" className="transition hover:text-brand">
            How it works
          </a>
          <a href="#features" className="transition hover:text-brand">
            Features
          </a>
        </div>

        <div className="flex items-center gap-3">
          <ThemeToggle />
          {auth.status === 'authenticated' ? (
            <Link to="/profile" aria-label="Your profile">
              <Avatar user={auth.user} />
            </Link>
          ) : (
            <Button onClick={loginWithGoogle} className="px-5 py-2 text-sm">
              Sign in
            </Button>
          )}
        </div>
      </nav>
    </motion.header>
  )
}
