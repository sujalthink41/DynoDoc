import confetti from 'canvas-confetti'

/** A short, brand-coloured confetti burst — fired when a learner passes a quiz. */
export function celebrate(): void {
  const colors = ['#6366f1', '#22c55e', '#f59e0b', '#ec4899']
  const fire = (particleRatio: number, opts: confetti.Options) => {
    void confetti({
      origin: { y: 0.7 },
      colors,
      particleCount: Math.floor(200 * particleRatio),
      ...opts,
    })
  }
  fire(0.25, { spread: 26, startVelocity: 55 })
  fire(0.2, { spread: 60 })
  fire(0.35, { spread: 100, decay: 0.91, scalar: 0.8 })
  fire(0.2, { spread: 120, startVelocity: 25, decay: 0.92, scalar: 1.2 })
}
