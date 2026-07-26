import { Link, useLocation } from 'react-router-dom'
import { HiShieldCheck, HiSun, HiMoon } from 'react-icons/hi2'
import { useTheme } from '../context/ThemeContext.jsx'

const STEPS = [
  { path: '/', label: 'Chat' },
  { path: '/confirmation', label: 'Confirmation' },
  { path: '/audit', label: 'Audit Trail' },
  { path: '/escalation', label: 'Escalation' },
]

export default function Header() {
  const location = useLocation()
  const activeIndex = STEPS.findIndex((s) => s.path === location.pathname)
  const { theme, toggleTheme } = useTheme()

  return (
    <header className="sticky top-0 z-30 bg-white/60 dark:bg-night-950/60 backdrop-blur-xl border-b border-white/50 dark:border-white/10 transition-colors duration-300">
      <div className="max-w-5xl mx-auto px-4 sm:px-6">
        <div className="h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2.5 group">
            <span className="flex h-9 w-9 items-center justify-center rounded-2xl bg-gradient-to-br from-primary-600 to-accent-500 text-white shadow-glow-primary transition-transform group-hover:scale-105">
              <HiShieldCheck className="h-5 w-5" />
            </span>
            <div className="leading-tight">
              <p className="text-[15px] font-bold text-ink-900 dark:text-white tracking-tight">
                ResolveAI
              </p>
              <p className="text-[11px] text-ink-500 dark:text-night-300 -mt-0.5">Banking Support</p>
            </div>
          </Link>

          <div className="flex items-center gap-3">
            <span className="hidden sm:flex items-center gap-1.5 text-xs font-medium text-ink-500 dark:text-night-300">
              <span className="h-1.5 w-1.5 rounded-full bg-success-500 animate-pulse" />
              Session secured
            </span>

            <button
              onClick={toggleTheme}
              aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
              className="relative flex h-9 w-9 items-center justify-center rounded-full bg-white/70 dark:bg-white/5
                border border-white/60 dark:border-white/10 text-ink-600 dark:text-accent-300 backdrop-blur-md
                shadow-glass dark:shadow-glass-dark transition-all duration-300 hover:-translate-y-0.5 hover:text-primary-600 dark:hover:text-primary-300"
            >
              <HiSun
                className={`absolute h-4.5 w-4.5 transition-all duration-300 ${
                  theme === 'dark' ? 'opacity-0 -rotate-90 scale-50' : 'opacity-100 rotate-0 scale-100'
                }`}
              />
              <HiMoon
                className={`absolute h-4.5 w-4.5 transition-all duration-300 ${
                  theme === 'dark' ? 'opacity-100 rotate-0 scale-100' : 'opacity-0 rotate-90 scale-50'
                }`}
              />
            </button>
          </div>
        </div>

        {/* Progress rail */}
        <div className="hidden md:flex items-center gap-2 pb-3 -mt-1">
          {STEPS.map((step, i) => (
            <div key={step.path} className="flex items-center gap-2 flex-1">
              <div className="flex items-center gap-2">
                <span
                  className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-[10px] font-bold transition-colors ${
                    i <= activeIndex
                      ? 'bg-gradient-to-br from-primary-600 to-accent-500 text-white'
                      : 'bg-ink-100 dark:bg-white/10 text-ink-400 dark:text-night-300'
                  }`}
                >
                  {i + 1}
                </span>
                <span
                  className={`text-xs font-medium whitespace-nowrap transition-colors ${
                    i <= activeIndex ? 'text-ink-800 dark:text-ink-100' : 'text-ink-400 dark:text-night-300'
                  }`}
                >
                  {step.label}
                </span>
              </div>
              {i < STEPS.length - 1 && (
                <span
                  className={`h-px flex-1 transition-colors ${
                    i < activeIndex ? 'bg-primary-400' : 'bg-ink-100 dark:bg-white/10'
                  }`}
                />
              )}
            </div>
          ))}
        </div>
      </div>
    </header>
  )
}
