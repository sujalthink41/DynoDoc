/** DynoCoin — the product's currency mark: a gold coin with a dino footprint. */
export function DynoCoin({ className = 'h-4 w-4' }: { className?: string }) {
  return (
    <svg viewBox="0 0 32 32" className={`inline-block shrink-0 ${className}`} aria-hidden>
      <defs>
        <linearGradient id="dynocoin-face" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#fde68a" />
          <stop offset="55%" stopColor="#fbbf24" />
          <stop offset="100%" stopColor="#f59e0b" />
        </linearGradient>
      </defs>
      <circle cx="16" cy="16" r="15" fill="url(#dynocoin-face)" stroke="#d97706" strokeWidth="1.5" />
      <circle cx="16" cy="16" r="11.5" fill="none" stroke="#ffffff" strokeWidth="1" opacity="0.45" />
      {/* three-toed dino footprint */}
      <g fill="#9a5b0e">
        <ellipse cx="16" cy="19.4" rx="4.2" ry="5" />
        <ellipse cx="10.8" cy="13.6" rx="1.7" ry="3.1" transform="rotate(-22 10.8 13.6)" />
        <ellipse cx="16" cy="11" rx="1.8" ry="3.4" />
        <ellipse cx="21.2" cy="13.6" rx="1.7" ry="3.1" transform="rotate(22 21.2 13.6)" />
      </g>
      {/* shine */}
      <ellipse cx="11.5" cy="10.5" rx="3.4" ry="2.1" fill="#ffffff" opacity="0.35" />
    </svg>
  )
}
