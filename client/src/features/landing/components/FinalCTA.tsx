import { motion } from 'framer-motion'

import { StartLearningButton } from '@/features/landing/components/StartLearningButton'

export function FinalCTA() {
  return (
    <section className="mx-auto max-w-5xl px-6 py-24">
      <motion.div
        initial={{ opacity: 0, scale: 0.97 }}
        whileInView={{ opacity: 1, scale: 1 }}
        viewport={{ once: true, margin: '-80px' }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
        className="relative overflow-hidden rounded-3xl border border-brand/20 bg-gradient-to-br from-brand/15 via-brand-2/10 to-brand-strong/10 px-8 py-16 text-center"
      >
        <h2 className="font-display text-3xl font-bold text-fg sm:text-4xl">
          Ready to learn something new?
        </h2>
        <p className="mx-auto mt-4 max-w-xl text-muted">
          Your personalized course is one question away.
        </p>
        <StartLearningButton className="mt-8 px-8 py-3.5">
          Start learning free →
        </StartLearningButton>
      </motion.div>
    </section>
  )
}
