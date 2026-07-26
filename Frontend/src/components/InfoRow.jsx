export default function InfoRow({ label, value, mono = false, highlight = false }) {
  return (
    <div className="flex items-center justify-between py-3.5">
      <span className="text-sm text-ink-500 dark:text-night-300">{label}</span>
      <span
        className={`text-sm text-right ${mono ? 'font-mono' : ''} ${
          highlight
            ? 'text-success-700 dark:text-success-400 font-bold text-base'
            : 'text-ink-900 dark:text-ink-100 font-semibold'
        }`}
      >
        {value}
      </span>
    </div>
  )
}
