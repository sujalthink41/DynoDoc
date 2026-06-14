import { useState } from 'react'
import { toast } from 'sonner'

import { Breadcrumb, HomeIcon } from '@/components/ui/Breadcrumb'
import { Card } from '@/components/ui/Card'
import { ConfirmDialog } from '@/components/ui/ConfirmDialog'
import { DynoCoin } from '@/components/ui/DynoCoin'
import { ProgressBar } from '@/components/ui/ProgressBar'
import { Spinner } from '@/components/ui/Spinner'
import { useRedeemReward, useRewards } from '@/features/game/queries'
import type { Reward } from '@/features/game/types'

function RewardCard({
  reward,
  coins,
  onRedeem,
}: {
  reward: Reward
  coins: number
  onRedeem: (r: Reward) => void
}) {
  const pct = Math.min(100, Math.round((coins / reward.cost) * 100))

  return (
    <Card
      className={`relative overflow-hidden p-6 text-center transition ${
        reward.claimed ? 'border-green-500/40' : 'hover:-translate-y-1 hover:border-brand/40'
      }`}
    >
      {reward.claimed && (
        <span className="absolute right-3 top-3 rounded-full bg-green-500/15 px-2.5 py-1 text-[0.65rem] font-bold uppercase text-green-500">
          Owned ✓
        </span>
      )}
      <span className={`text-6xl ${reward.claimed || reward.affordable ? '' : 'opacity-40 grayscale'}`}>
        {reward.emoji}
      </span>
      <h3 className="mt-3 font-display text-lg font-semibold text-fg">{reward.title}</h3>
      <p className="mt-1 flex items-center justify-center gap-1 text-sm font-semibold text-amber-500">
        <DynoCoin className="h-4 w-4" /> {reward.cost.toLocaleString()}
      </p>

      {reward.claimed ? (
        <p className="mt-5 text-sm font-medium text-green-500">Redeemed</p>
      ) : reward.affordable ? (
        <button
          type="button"
          onClick={() => onRedeem(reward)}
          className="mt-5 w-full rounded-full bg-gradient-to-r from-brand to-brand-2 px-4 py-2.5 text-sm font-semibold text-white shadow-md shadow-brand/30 transition hover:-translate-y-0.5"
        >
          Redeem
        </button>
      ) : (
        <div className="mt-5">
          <ProgressBar value={pct} />
          <p className="mt-1.5 text-xs text-muted">
            {coins.toLocaleString()} / {reward.cost.toLocaleString()} ({pct}%)
          </p>
        </div>
      )}
    </Card>
  )
}

export function RewardsPage() {
  const { data, isPending } = useRewards(true)
  const redeem = useRedeemReward()
  const [pending, setPending] = useState<Reward | null>(null)
  const [address, setAddress] = useState('')

  const openRedeem = (reward: Reward) => {
    setAddress('')
    setPending(reward)
  }

  const confirmRedeem = () => {
    if (!pending || address.trim().length < 10) return
    const reward = pending
    redeem.mutate(
      { key: reward.key, address: address.trim() },
      {
        onSuccess: () => {
          setPending(null)
          toast.success(`🎉 Redeemed ${reward.title}! We'll ship it to your address soon.`)
        },
        onError: () => toast.error('Could not redeem. Check your address and try again.'),
      },
    )
  }

  return (
    <main>
      <Breadcrumb
        items={[
          { label: 'Home', to: '/app', icon: <HomeIcon /> },
          { label: 'Games', to: '/games' },
          { label: 'Rewards' },
        ]}
      />

      <div className="mt-6 flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="font-display text-3xl font-bold text-fg sm:text-4xl">🎁 Rewards Shop</h1>
          <p className="mt-2 text-muted">Spend your DynoCoins on real DynoDoc swag.</p>
        </div>
        {data && (
          <div className="flex items-center gap-2 rounded-2xl border border-line bg-elevated/70 px-4 py-2.5 backdrop-blur-xl">
            <DynoCoin className="h-6 w-6" />
            <span className="font-display text-xl font-bold text-amber-500">
              {data.coins.toLocaleString()}
            </span>
            <span className="text-sm text-muted">to spend</span>
          </div>
        )}
      </div>

      {isPending || !data ? (
        <div className="flex justify-center py-16">
          <Spinner />
        </div>
      ) : (
        <div className="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {data.rewards.map((reward) => (
            <RewardCard key={reward.key} reward={reward} coins={data.coins} onRedeem={openRedeem} />
          ))}
        </div>
      )}

      <ConfirmDialog
        open={pending !== null}
        title={`Redeem ${pending?.title ?? ''}?`}
        body={
          <span className="flex items-center gap-1">
            Spends <DynoCoin className="h-4 w-4" /> {pending?.cost.toLocaleString()} from your
            balance. Where should we ship it?
          </span>
        }
        confirmLabel="Redeem & ship"
        busy={redeem.isPending}
        confirmDisabled={address.trim().length < 10}
        onConfirm={confirmRedeem}
        onCancel={() => setPending(null)}
      >
        <textarea
          value={address}
          onChange={(e) => setAddress(e.target.value)}
          rows={4}
          placeholder="Full name, street address, city, state, ZIP, country, phone"
          className="w-full resize-none rounded-xl border border-line bg-surface px-4 py-2.5 text-sm text-fg placeholder:text-muted focus:border-brand/50 focus:outline-none"
        />
      </ConfirmDialog>

      <p className="mt-6 text-center text-xs text-muted">
        Redeeming deducts the coins from your balance. Lifetime earnings (your leaderboard rank)
        aren't affected.
      </p>
    </main>
  )
}
