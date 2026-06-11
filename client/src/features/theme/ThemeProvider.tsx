import { useCallback, useEffect, useState, type ReactNode } from 'react'

import { ThemeContext, type Theme } from '@/features/theme/context'

function initialTheme(): Theme {
  const saved = localStorage.getItem('theme')
  return saved === 'light' || saved === 'dark' ? saved : 'dark'
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>(initialTheme)

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark')
    localStorage.setItem('theme', theme)
  }, [theme])

  const toggle = useCallback(() => {
    setTheme((current) => (current === 'dark' ? 'light' : 'dark'))
  }, [])

  return <ThemeContext.Provider value={{ theme, toggle }}>{children}</ThemeContext.Provider>
}
