import type { ReactNode } from 'react'

import { Button } from '@/components/ui/Button'

interface ConfirmDialogProps {
  open: boolean
  title: string
  body?: ReactNode
  children?: ReactNode
  confirmLabel?: string
  cancelLabel?: string
  busy?: boolean
  confirmDisabled?: boolean
  onConfirm: () => void
  onCancel: () => void
}

/** A shared confirm modal — used for every coin redemption (rewards, slots, unlocks). */
export function ConfirmDialog({
  open,
  title,
  body,
  children,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  busy,
  confirmDisabled,
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  if (!open) return null
  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center p-4">
      <button
        type="button"
        aria-label="Cancel"
        onClick={onCancel}
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
      />
      <div className="animate-pop-in relative w-full max-w-sm rounded-3xl border border-line bg-elevated p-6 shadow-2xl">
        <h3 className="font-display text-lg font-bold text-fg">{title}</h3>
        {body && <div className="mt-2 text-sm text-muted">{body}</div>}
        {children && <div className="mt-4">{children}</div>}
        <div className="mt-6 flex justify-end gap-2">
          <Button variant="ghost" onClick={onCancel} disabled={busy} className="px-4 py-2.5">
            {cancelLabel}
          </Button>
          <Button
            onClick={onConfirm}
            disabled={busy || confirmDisabled}
            className="px-5 py-2.5"
          >
            {busy ? 'Working…' : confirmLabel}
          </Button>
        </div>
      </div>
    </div>
  )
}
