export default function GradientBackdrop() {
  return (
    <div className="fixed inset-0 -z-10 overflow-hidden bg-ink-50 dark:bg-night-950 transition-colors duration-500">
      {/* Light mode blobs */}
      <div className="absolute inset-0 opacity-100 dark:opacity-0 transition-opacity duration-500">
        <div className="absolute -top-32 -left-24 h-[420px] w-[420px] rounded-full bg-primary-200/60 blur-[100px]" />
        <div className="absolute top-1/3 -right-32 h-[460px] w-[460px] rounded-full bg-accent-200/50 blur-[110px]" />
        <div className="absolute bottom-0 left-1/4 h-[380px] w-[380px] rounded-full bg-blush-200/50 blur-[100px]" />
        <div className="absolute bottom-10 right-10 h-[300px] w-[300px] rounded-full bg-success-100/60 blur-[90px]" />
      </div>

      {/* Dark mode blobs */}
      <div className="absolute inset-0 opacity-0 dark:opacity-100 transition-opacity duration-500">
        <div className="absolute -top-32 -left-24 h-[420px] w-[420px] rounded-full bg-primary-700/25 blur-[110px]" />
        <div className="absolute top-1/3 -right-32 h-[460px] w-[460px] rounded-full bg-accent-600/25 blur-[120px]" />
        <div className="absolute bottom-0 left-1/4 h-[380px] w-[380px] rounded-full bg-blush-400/10 blur-[110px]" />
        <div className="absolute bottom-10 right-10 h-[300px] w-[300px] rounded-full bg-success-600/15 blur-[100px]" />
      </div>

      {/* Soft top-to-bottom fade so content stays readable */}
      <div className="absolute inset-0 bg-gradient-to-b from-white/40 via-white/10 to-white/40 dark:from-night-950/50 dark:via-night-950/10 dark:to-night-950/60" />
    </div>
  )
}
