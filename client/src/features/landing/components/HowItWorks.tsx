import { motion } from 'framer-motion'

const STEPS = [
  { n: '01', title: 'Tell us your goal', desc: '“I want to learn Python.” A few quick questions tune the course to you.' },
  { n: '02', title: 'Get your course', desc: 'AI designs a roadmap and writes the lessons — made for your level and pace.' },
  { n: '03', title: 'Learn & prove it', desc: 'Read, build, get checked, and watch your real progress add up.' },
]

export function HowItWorks() {
  return (
    <section id="how" className="mx-auto max-w-6xl px-6 py-24">
      <div className="mx-auto max-w-2xl text-center">
        <h2 className="font-display text-3xl font-bold text-fg sm:text-4xl">
          From curious to capable in 3 steps
        </h2>
      </div>
      <div className="mt-14 grid gap-10 md:grid-cols-3">
        {STEPS.map((step, i) => (
          <motion.div
            key={step.n}
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-80px' }}
            transition={{ delay: i * 0.1, duration: 0.5, ease: 'easeOut' }}
          >
            <span className="font-display text-5xl font-bold text-brand/25">{step.n}</span>
            <h3 className="mt-2 font-display text-xl font-semibold text-fg">{step.title}</h3>
            <p className="mt-2 text-muted">{step.desc}</p>
          </motion.div>
        ))}
      </div>
    </section>
  )
}
