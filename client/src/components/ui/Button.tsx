import type { ButtonHTMLAttributes } from 'react'

type Variant = 'primary' | 'ghost'

const VARIANTS: Record<Variant, string> = {
  primary:
    'bg-gradient-to-r from-brand to-brand-2 text-white shadow-lg shadow-brand/30 hover:-translate-y-0.5 hover:shadow-brand/50',
  ghost: 'text-muted ring-1 ring-line hover:bg-surface hover:text-fg',
}

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
}

export function Button({ variant = 'primary', className = '', ...props }: ButtonProps) {
  return (
    <button
      {...props}
      className={`inline-flex items-center justify-center gap-2 rounded-full font-semibold transition disabled:cursor-not-allowed disabled:opacity-60 ${VARIANTS[variant]} ${className}`}
    />
  )
}
