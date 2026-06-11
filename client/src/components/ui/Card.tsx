import type { HTMLAttributes } from 'react'

export function Card({ className = '', ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      {...props}
      className={`rounded-3xl border border-line bg-elevated shadow-xl backdrop-blur-xl ${className}`}
    />
  )
}
