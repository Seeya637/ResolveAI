import { HiCheck } from 'react-icons/hi2'

export default function TimelineStep({ title, description, timestamp, isLast, delay = 0 }) {
  return (
    <div className="relative flex gap-4 animate-fadeUp" style={{ animationDelay: `${delay}ms` }}>
      <div className="flex flex-col items-center">
        <span className="relative flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-success-500 to-success-700 text-white shadow-sm ring-4 ring-success-50 dark:ring-success-500/10">
          <HiCheck className="h-4.5 w-4.5" strokeWidth={1} />
        </span>
        {!isLast && <span className="w-px flex-1 bg-ink-200 dark:bg-white/10 my-1" />}
      </div>

      <div className={`${isLast ? '' : 'pb-8'} pt-1 flex-1`}>
        <div className="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-0.5">
          <p className="text-sm font-semibold text-ink-900 dark:text-ink-100">{title}</p>
          <span className="font-mono text-xs text-ink-400 dark:text-night-300">{timestamp}</span>
        </div>
        {description && (
          <p className="mt-1 text-sm text-ink-500 dark:text-night-300">{description}</p>
        )}
      </div>
    </div>
  )
}
