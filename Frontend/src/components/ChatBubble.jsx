import { HiShieldCheck } from 'react-icons/hi2'

export default function ChatBubble({ from, children, delay = 0, emphasis = false }) {
  const isCustomer = from === 'customer'

  return (
    <div
      className={`flex items-end gap-2.5 ${isCustomer ? 'flex-row-reverse' : 'flex-row'} animate-fadeUp`}
      style={{ animationDelay: `${delay}ms` }}
    >
      {!isCustomer && (
        <span className="mb-1 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-primary-600 to-accent-500 text-white shadow-sm">
          <HiShieldCheck className="h-4 w-4" />
        </span>
      )}

      <div
        className={`max-w-[80%] sm:max-w-[70%] rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-sm backdrop-blur-sm ${
          isCustomer
            ? 'bg-gradient-to-br from-primary-600 to-accent-500 text-white rounded-br-md'
            : emphasis
              ? 'bg-success-50/90 dark:bg-success-600/10 text-success-800 dark:text-success-300 border border-success-100 dark:border-success-600/20 rounded-bl-md font-medium'
              : 'bg-white/80 dark:bg-white/5 text-ink-800 dark:text-ink-100 border border-white/60 dark:border-white/10 rounded-bl-md'
        }`}
      >
        {children}
      </div>
    </div>
  )
}
