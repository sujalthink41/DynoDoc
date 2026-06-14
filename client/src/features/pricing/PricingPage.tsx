import { Link } from 'react-router-dom'
import { toast } from 'sonner'

import { Breadcrumb, HomeIcon } from '@/components/ui/Breadcrumb'

interface Plan {
  name: string
  price: string
  period: string
  tagline: string
  courses: string
  features: string[]
  highlight?: boolean
  cta: string
}

const PLANS: Plan[] = [
  {
    name: 'Free',
    price: '$0',
    period: 'forever',
    tagline: 'Get going, no strings.',
    courses: '3 roadmaps',
    features: [
      '3 AI-built course roadmaps',
      'Daily Connections game',
      'DynoCoins, streaks & leaderboards',
      'In-lesson AI tutor',
    ],
    cta: 'Your current plan',
  },
  {
    name: 'Weekly',
    price: '$2.99',
    period: '/ week',
    tagline: 'Crunch-time learning.',
    courses: '10 roadmaps',
    features: [
      'Everything in Free',
      'Up to 10 roadmaps',
      'Priority lesson generation',
      'Cancel anytime',
    ],
    cta: 'Go Weekly',
  },
  {
    name: 'Monthly',
    price: '$7.99',
    period: '/ month',
    tagline: 'The serious learner’s pick.',
    courses: '40 roadmaps',
    features: [
      'Everything in Weekly',
      'Up to 40 roadmaps',
      'Priority generation & tutor',
      'Early access to new games',
    ],
    highlight: true,
    cta: 'Go Monthly',
  },
]

function PlanCard({ plan }: { plan: Plan }) {
  const upgrade = () =>
    plan.name === 'Free'
      ? undefined
      : toast.success("Payments are coming soon — you'll be the first to know! 🚀")

  return (
    <div
      className={`relative flex flex-col rounded-3xl border p-7 transition ${
        plan.highlight
          ? 'border-brand/50 bg-gradient-to-br from-brand/10 to-brand-2/10 shadow-2xl shadow-brand/10 lg:-translate-y-3'
          : 'border-line bg-elevated/70 backdrop-blur-xl hover:-translate-y-1 hover:border-brand/30'
      }`}
    >
      {plan.highlight && (
        <span className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-gradient-to-r from-brand to-brand-2 px-3 py-1 text-xs font-bold uppercase tracking-wide text-white shadow-md">
          Most popular
        </span>
      )}
      <h3 className="font-display text-xl font-bold text-fg">{plan.name}</h3>
      <p className="mt-1 text-sm text-muted">{plan.tagline}</p>
      <div className="mt-5 flex items-end gap-1">
        <span className="font-display text-4xl font-bold text-fg">{plan.price}</span>
        <span className="mb-1 text-sm text-muted">{plan.period}</span>
      </div>
      <p className="mt-1 text-sm font-semibold text-brand">{plan.courses}</p>

      <ul className="mt-6 flex-1 space-y-2.5">
        {plan.features.map((f) => (
          <li key={f} className="flex items-start gap-2 text-sm text-fg">
            <span className="mt-0.5 text-brand">✓</span>
            {f}
          </li>
        ))}
      </ul>

      <button
        type="button"
        onClick={upgrade}
        disabled={plan.name === 'Free'}
        className={`mt-7 w-full rounded-full px-5 py-3 text-sm font-semibold transition ${
          plan.name === 'Free'
            ? 'cursor-default border border-line text-muted'
            : plan.highlight
              ? 'bg-gradient-to-r from-brand to-brand-2 text-white shadow-lg shadow-brand/30 hover:-translate-y-0.5'
              : 'border border-brand/40 text-brand hover:bg-brand/10'
        }`}
      >
        {plan.cta}
      </button>
    </div>
  )
}

export function PricingPage() {
  return (
    <main>
      <Breadcrumb items={[{ label: 'Home', to: '/app', icon: <HomeIcon /> }, { label: 'Pricing' }]} />

      <div className="mt-8 text-center">
        <span className="inline-flex items-center gap-1.5 rounded-full border border-brand/30 bg-brand/10 px-3 py-1 text-xs font-semibold text-brand">
          🦖 DynoDoc Pro
        </span>
        <h1 className="mt-4 font-display text-4xl font-bold tracking-tight text-fg sm:text-5xl">
          Learn without{' '}
          <span className="bg-gradient-to-r from-brand to-brand-2 bg-clip-text text-transparent">
            limits
          </span>
        </h1>
        <p className="mx-auto mt-3 max-w-md text-muted">
          Start free with 3 roadmaps. Upgrade when you're ready to build more — cancel anytime.
        </p>
      </div>

      <div className="mt-12 grid gap-6 lg:grid-cols-3 lg:items-center">
        {PLANS.map((plan) => (
          <PlanCard key={plan.name} plan={plan} />
        ))}
      </div>

      <p className="mt-10 text-center text-xs text-muted">
        Prices in USD. Your DynoCoins, streaks, and existing courses always stay with you.{' '}
        <Link to="/games/rewards" className="text-brand hover:underline">
          Spend coins on rewards →
        </Link>
      </p>
    </main>
  )
}
