import { motion } from 'framer-motion'

const FEATURES = [
  { icon: '🧭', title: 'Personalized roadmap', desc: 'Answer a few questions and get a course mapped to your level, goal, and pace.' },
  { icon: '✍️', title: 'Lessons written for you', desc: 'Every lesson is generated for how you learn — go simpler or deeper on demand.' },
  { icon: '🛠️', title: 'Learn by doing', desc: 'Quizzes and hands-on tasks, checked by AI — proof you actually learned it.' },
  { icon: '🔗', title: 'Best of the web', desc: 'Curated articles and videos for every topic, so you never get lost again.' },
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
      <div className="mt-16 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
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
