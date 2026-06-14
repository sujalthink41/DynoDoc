import { motion } from 'framer-motion'

const FEATURES = [
  { icon: '🧭', title: 'Roadmap sized to your goal', desc: 'A focused 3-lesson explainer or a full career path — the AI builds exactly what your goal needs, no filler.' },
  { icon: '✍️', title: 'Lessons written for you', desc: 'Every lesson is generated for your level and intent — concise where it can be, deep where it counts.' },
  { icon: '💬', title: 'Ask DynoDoc anytime', desc: 'A built-in AI tutor that knows your exact lesson — ask follow-ups and get grounded answers, in context.' },
  { icon: '✅', title: 'Prove it to unlock', desc: 'Pass a quiz to move on, hit 100% to master a lesson. Real checkpoints, not just videos you scrub past.' },
  { icon: '🎮', title: 'Learn, play, earn', desc: 'A daily puzzle, streaks, and DynoCoins for every win — climb the leaderboard and redeem coins for merch.' },
  { icon: '📈', title: 'Progress you can feel', desc: 'Badges, mastery, and streaks track how far you’ve come — and keep you coming back.' },
]

export function Features() {
  return (
    <section id="features" className="mx-auto max-w-6xl px-6 py-24">
      <div className="mx-auto max-w-2xl text-center">
        <h2 className="font-display text-3xl font-bold text-fg sm:text-4xl">
          Learning that adapts to you
        </h2>
        <p className="mt-4 text-muted">
          Not another pile of videos — a path built around your goal, and only yours.
        </p>
      </div>
      <div className="mt-16 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {FEATURES.map((feature, i) => (
          <motion.div
            key={feature.title}
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-80px' }}
            transition={{ duration: 0.5, delay: i * 0.08, ease: 'easeOut' }}
            className="group rounded-2xl border border-line bg-surface p-6 transition hover:-translate-y-1 hover:border-brand/40"
          >
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-brand/20 to-brand-2/20 text-2xl ring-1 ring-brand/20">
              {feature.icon}
            </div>
            <h3 className="mt-5 font-display text-lg font-semibold text-fg">{feature.title}</h3>
            <p className="mt-2 text-sm leading-relaxed text-muted">{feature.desc}</p>
          </motion.div>
        ))}
      </div>
    </section>
  )
}
