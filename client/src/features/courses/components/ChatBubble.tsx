import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

interface ChatBubbleProps {
  role: 'user' | 'assistant'
  content: string
  userInitial?: string
  /** Render assistant content as Markdown (used by the lesson tutor). */
  markdown?: boolean
}

function Avatar({ role, userInitial }: { role: 'user' | 'assistant'; userInitial?: string }) {
  if (role === 'assistant') {
    return (
      <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-brand to-brand-2 font-display text-sm font-bold text-white shadow-md shadow-brand/30">
        D
      </span>
    )
  }
  return (
    <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl border border-line bg-surface text-sm font-semibold text-muted">
      {userInitial ?? 'You'.charAt(0)}
    </span>
  )
}

export function ChatBubble({ role, content, userInitial, markdown }: ChatBubbleProps) {
  const isUser = role === 'user'
  const renderMarkdown = markdown && !isUser
  return (
    <div className={`flex items-end gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      <Avatar role={role} userInitial={userInitial} />
      <div
        className={
          isUser
            ? 'max-w-[80%] whitespace-pre-line rounded-2xl rounded-br-md bg-gradient-to-r from-brand to-brand-2 px-4 py-2.5 text-[0.95rem] leading-relaxed text-white shadow-md shadow-brand/20'
            : 'max-w-[85%] rounded-2xl rounded-bl-md border border-line bg-elevated px-4 py-2.5 text-[0.95rem] leading-relaxed text-fg shadow-sm'
        }
      >
        {renderMarkdown ? (
          <div className="prose prose-sm prose-slate max-w-none dark:prose-invert prose-p:my-1.5 prose-pre:my-2 prose-headings:font-display prose-a:text-brand">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
          </div>
        ) : (
          <span className="whitespace-pre-line">{content}</span>
        )}
      </div>
    </div>
  )
}
