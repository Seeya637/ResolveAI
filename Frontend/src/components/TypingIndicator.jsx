import { HiShieldCheck } from 'react-icons/hi2'

export default function TypingIndicator({ delay = 0 }) {
  return (
    <div className="flex items-end gap-2.5 animate-fadeUp" style={{ animationDelay: `${delay}ms` }}>
      <span className="mb-1 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-primary-600 to-accent-500 text-white shadow-sm">
        <HiShieldCheck className="h-4 w-4" />
      </span>
      <div className="flex items-center gap-1 rounded-2xl rounded-bl-md border border-white/60 dark:border-white/10 bg-white/80 dark:bg-white/5 px-4 py-3.5 shadow-sm backdrop-blur-sm">
        {[0, 1, 2].map((i) => (
          <span
            key={i}
            className="h-1.5 w-1.5 rounded-full bg-ink-300 dark:bg-night-300 animate-bounce"
            style={{ animationDelay: `${i * 120}ms` }}
          />
        ))}
      </div>
    </div>
  )
}
