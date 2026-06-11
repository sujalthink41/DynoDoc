/** Animated brand-red gradient blobs + a faint theme-aware grid behind the hero. */
export function AuroraBackground() {
  return (
    <div className="pointer-events-none absolute inset-0 -z-10 overflow-hidden">
      <div className="animate-blob absolute -left-32 -top-40 h-[36rem] w-[36rem] rounded-full bg-brand/25 blur-3xl" />
      <div className="animate-blob animation-delay-2000 absolute -right-20 top-10 h-[34rem] w-[34rem] rounded-full bg-brand-2/20 blur-3xl" />
      <div className="animate-blob animation-delay-4000 absolute bottom-0 left-1/3 h-[30rem] w-[30rem] rounded-full bg-brand-strong/15 blur-3xl" />
      <div
        className="absolute inset-0 text-fg/[0.06]"
        style={{
          backgroundImage:
            'linear-gradient(to right, currentColor 1px, transparent 1px), linear-gradient(to bottom, currentColor 1px, transparent 1px)',
          backgroundSize: '46px 46px',
          maskImage: 'radial-gradient(ellipse at center, black, transparent 70%)',
          WebkitMaskImage: 'radial-gradient(ellipse at center, black, transparent 70%)',
        }}
      />
    </div>
  )
}
