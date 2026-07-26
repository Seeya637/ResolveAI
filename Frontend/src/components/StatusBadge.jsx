import { HiCheckCircle, HiClock, HiArrowPath } from 'react-icons/hi2'

const VARIANTS = {
  success: {
    icon: HiCheckCircle,
    classes: 'bg-success-50 dark:bg-success-600/10 text-success-700 dark:text-success-400 border-success-100 dark:border-success-600/20',
  },
  pending: {
    icon: HiClock,
    classes: 'bg-amber-50 dark:bg-amber-500/10 text-amber-700 dark:text-amber-400 border-amber-100 dark:border-amber-500/20',
  },
  progress: {
    icon: HiArrowPath,
    classes: 'bg-primary-50 dark:bg-primary-500/10 text-primary-700 dark:text-primary-300 border-primary-100 dark:border-primary-500/20',
  },
}

export default function StatusBadge({ label, variant = 'success' }) {
  const { icon: Icon, classes } = VARIANTS[variant] ?? VARIANTS.success

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-semibold backdrop-blur-sm ${classes}`}
    >
      <Icon className="h-3.5 w-3.5" />
      {label}
    </span>
  )
}
