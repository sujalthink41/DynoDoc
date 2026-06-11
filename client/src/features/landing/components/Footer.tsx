export function Footer() {
  return (
    <footer className="border-t border-line px-6 py-10">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 text-sm text-muted sm:flex-row">
        <div className="flex items-center gap-2">
          <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-gradient-to-br from-brand to-brand-2 font-display text-sm font-bold text-white">
            D
          </span>
          <span className="font-display font-semibold text-fg">DynoDoc</span>
        </div>
        <p>© 2026 DynoDoc · Learn anything, your way.</p>
      </div>
    </footer>
  )
}
