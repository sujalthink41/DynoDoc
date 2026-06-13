import { Fragment, type ReactNode } from 'react'
import { Link } from 'react-router-dom'

export interface Crumb {
  label: string
  to?: string
  icon?: ReactNode
}

function HomeIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      className="h-4 w-4"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
    >
      <path d="M3 10.5 12 3l9 7.5" />
      <path d="M5 9.5V21h14V9.5" />
    </svg>
  )
}

function Chevron() {
  return (
    <svg
      viewBox="0 0 24 24"
      className="h-3.5 w-3.5 text-muted/50"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
    >
      <path d="m9 18 6-6-6-6" />
    </svg>
  )
}

export { HomeIcon }

export function Breadcrumb({ items }: { items: Crumb[] }) {
  return (
    <nav aria-label="Breadcrumb" className="flex flex-wrap items-center gap-1.5 text-sm">
      {items.map((item, i) => {
        const isLast = i === items.length - 1
        const content = (
          <span className="flex items-center gap-1.5">
            {item.icon}
            <span className="max-w-[14rem] truncate">{item.label}</span>
          </span>
        )
        return (
          <Fragment key={i}>
            {i > 0 && <Chevron />}
            {item.to && !isLast ? (
              <Link
                to={item.to}
                className="flex items-center gap-1.5 rounded-md px-1.5 py-0.5 text-muted transition hover:bg-surface hover:text-fg"
              >
                {content}
              </Link>
            ) : (
              <span className={`px-1.5 py-0.5 ${isLast ? 'font-medium text-fg' : 'text-muted'}`}>
                {content}
              </span>
            )}
          </Fragment>
        )
      })}
    </nav>
  )
}
