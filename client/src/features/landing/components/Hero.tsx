import { motion, type Variants } from 'framer-motion'
import { useEffect, useState } from 'react'

import { AIThinking } from '@/components/ui/AIThinking'
import { Card } from '@/components/ui/Card'
import { StartLearningButton } from '@/features/landing/components/StartLearningButton'

const container: Variants = {
  hidden: {},
  show: { transition: { staggerChildren: 0.12, delayChildren: 0.1 } },
}

const item: Variants = {
  hidden: { y: 24, opacity: 0 },
  show: { y: 0, opacity: 1, transition: { duration: 0.6, ease: 'easeOut' } },
}

const DEMOS = [
  {
    prompt: 'I want to learn Python to automate my spreadsheets.',
    roadmap: ['Python fundamentals', 'Working with data', 'Automating spreadsheets', 'Build a real project'],
  },
  {
    prompt: 'I want to get good at React and ship real apps.',
    roadmap: ['JavaScript essentials', 'Components & state', 'Hooks & data fetching', 'Ship a real app'],
  },
  {
    prompt: 'I want to learn machine learning from scratch.',
    roadmap: ['The math you actually need', 'Python for ML', 'Core ML algorithms', 'Train your first model'],
  },
  {
    prompt: 'I want to master public speaking.',
    roadmap: ['Beat the fear', 'Structure a talk', 'Delivery & presence', 'Give a real talk'],
  },
  {
    prompt: 'I want to learn guitar in 3 months.',
    roadmap: ['Chords & strumming', 'Reading tabs', 'Your first songs', 'Play a full song'],
  },
]

type Phase = 'typing' | 'thinking' | 'roadmap'

function HeroMock() {
  const [demo, setDemo] = useState(0)
  const [typed, setTyped] = useState('')
  const [phase, setPhase] = useState<Phase>('typing')
  const [shown, setShown] = useState(0)
  const current = DEMOS[demo]

  useEffect(() => {
    if (phase !== 'typing') return
    if (typed.length < current.prompt.length) {
      const t = setTimeout(() => setTyped(current.prompt.slice(0, typed.length + 1)), 45)
      return () => clearTimeout(t)
    }
    const t = setTimeout(() => setPhase('thinking'), 700)
    return () => clearTimeout(t)
  }, [typed, phase, current.prompt])

  useEffect(() => {
    if (phase !== 'thinking') return
    const t = setTimeout(() => setPhase('roadmap'), 1500)
    return () => clearTimeout(t)
  }, [phase])

  useEffect(() => {
    if (phase !== 'roadmap') return
    if (shown < current.roadmap.length) {
      const t = setTimeout(() => setShown((s) => s + 1), 340)
      return () => clearTimeout(t)
    }
    const t = setTimeout(() => {
      setTyped('')
      setShown(0)
      setDemo((d) => (d + 1) % DEMOS.length)
      setPhase('typing')
    }, 2800)
    return () => clearTimeout(t)
  }, [phase, shown, current.roadmap.length])

  return (
    <motion.div
      initial={{ opacity: 0, y: 40, scale: 0.96 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ delay: 0.6, duration: 0.8, ease: 'easeOut' }}
      className="relative mt-20 w-full max-w-2xl"
    >
      <Card className="animate-float p-5">
        <div className="flex items-center gap-2 pb-4">
          <span className="h-3 w-3 rounded-full bg-brand/60" />
          <span className="h-3 w-3 rounded-full bg-amber-400/70" />
          <span className="h-3 w-3 rounded-full bg-emerald-400/70" />
        </div>

        <div className="rounded-2xl bg-fg/[0.04] p-4 text-left">
          <p className="text-xs uppercase tracking-wider text-muted">You</p>
          <p className="mt-1 min-h-6 text-fg">
            {typed}
            {phase === 'typing' && <span className="animate-caret text-brand">|</span>}
          </p>
        </div>

        {phase === 'thinking' && (
          <div className="mt-3">
            <AIThinking label="DynoDoc is building your roadmap…" />
          </div>
        )}

        {phase === 'roadmap' && (
          <div className="mt-3 rounded-2xl bg-gradient-to-br from-brand/10 to-brand-2/10 p-4 text-left ring-1 ring-brand/20">
            <p className="text-xs uppercase tracking-wider text-brand">Your roadmap</p>
            <ul className="mt-2 space-y-2">
              {current.roadmap.slice(0, shown).map((lecture, i) => (
                <motion.li
                  key={lecture}
                  initial={{ opacity: 0, x: -12 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ ease: 'easeOut' }}
                  className="flex items-center gap-3 text-sm text-fg"
                >
                  <span className="flex h-6 w-6 items-center justify-center rounded-lg bg-brand/15 text-xs font-semibold text-brand">
                    {i + 1}
                  </span>
                  {lecture}
                </motion.li>
              ))}
            </ul>
          </div>
        )}
      </Card>
    </motion.div>
  )
}

export function Hero() {
  return (
    <section className="relative mx-auto flex max-w-6xl flex-col items-center px-6 pb-24 pt-40 text-center">
      <motion.div variants={container} initial="hidden" animate="show" className="flex flex-col items-center">
        <motion.span
          variants={item}
          className="mb-6 inline-flex items-center gap-2 rounded-full border border-line bg-surface px-4 py-1.5 text-xs font-medium text-muted backdrop-blur"
        >
          <span className="h-1.5 w-1.5 rounded-full bg-brand" />
          AI-native learning, built for you
        </motion.span>

        <motion.h1
          variants={item}
          className="font-display text-5xl font-bold leading-[1.05] tracking-tight text-fg sm:text-7xl"
        >
          Master anything.
          <br />
          <span className="text-shimmer bg-gradient-to-r from-brand-2 via-brand to-brand-strong bg-clip-text text-transparent">
            Your AI builds the path.
          </span>
        </motion.h1>

        <motion.p variants={item} className="mt-6 max-w-2xl text-lg text-muted">
          Tell DynoDoc what you want to learn. Get a personalized course — lessons written for{' '}
          <em className="text-fg">your</em> level, hands-on tasks, and the best resources on the
          web. Learning that finally feels made for you.
        </motion.p>

        <motion.div variants={item} className="mt-10 flex flex-col items-center gap-4 sm:flex-row">
          <StartLearningButton className="group px-8 py-3.5">
            Start learning free
            <span className="transition group-hover:translate-x-1">→</span>
          </StartLearningButton>
          <a
            href="#how"
            className="rounded-full px-6 py-3.5 font-medium text-muted ring-1 ring-line transition hover:bg-surface hover:text-fg"
          >
            See how it works
          </a>
        </motion.div>

        <motion.p variants={item} className="mt-4 text-xs text-muted">
          Free to start · Sign in with Google · No credit card
        </motion.p>
      </motion.div>

      <HeroMock />
    </section>
  )
}
