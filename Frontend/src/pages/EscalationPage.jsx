import { useNavigate } from 'react-router-dom'
import { HiOutlineUserCircle, HiOutlineClock, HiHome } from 'react-icons/hi2'
import PageContainer from '../components/PageContainer.jsx'
import InfoRow from '../components/InfoRow.jsx'
import StatusBadge from '../components/StatusBadge.jsx'

export default function EscalationPage() {
  const navigate = useNavigate()

  return (
    <PageContainer className="max-w-md">
      <div className="card overflow-hidden">
        <div className="flex flex-col items-center gap-4 px-6 pt-9 pb-7 text-center">
          <div className="relative flex h-20 w-20 items-center justify-center">
            <span className="absolute inset-0 rounded-full bg-primary-500/20 animate-pulseRing" />
            <span className="relative flex h-20 w-20 items-center justify-center rounded-full bg-gradient-to-br from-primary-600 to-accent-500 shadow-pop animate-popIn">
              <HiOutlineUserCircle className="h-10 w-10 text-white" />
            </span>
          </div>

          <div>
            <h1 className="text-lg font-bold text-ink-900 dark:text-white">You're in good hands</h1>
            <p className="mt-2 text-sm text-ink-500 dark:text-night-300 leading-relaxed max-w-xs">
              Your request requires additional review. All conversation history and verification
              details have been securely transferred to a banking specialist.
            </p>
          </div>

          <StatusBadge label="Transferred to Banking Specialist" variant="progress" />
        </div>

        <div className="px-6 py-2 divide-y divide-ink-100 dark:divide-white/10 border-t border-ink-100 dark:border-white/10">
          <InfoRow label="Case ID" value="CASE-48291" mono />
          <InfoRow label="Status" value="Transferred to Banking Specialist" />
          <InfoRow
            label="Est. Response Time"
            value={
              <span className="inline-flex items-center gap-1.5">
                <HiOutlineClock className="h-4 w-4 text-primary-600 dark:text-primary-300" />
                5 minutes
              </span>
            }
          />
        </div>

        <div className="mx-6 mb-6 mt-4 rounded-2xl bg-ink-50/80 dark:bg-white/[0.03] border border-ink-100 dark:border-white/10 px-4 py-3.5 backdrop-blur-sm">
          <p className="text-xs leading-relaxed text-ink-500 dark:text-night-300">
            You don't need to repeat anything. A specialist will pick up the full context of your
            case and reach out shortly.
          </p>
        </div>

        <div className="px-6 pb-6">
          <button onClick={() => navigate('/')} className="btn-primary w-full">
            <HiHome className="h-4 w-4" />
            Back to Home
          </button>
        </div>
      </div>
    </PageContainer>
  )
}
