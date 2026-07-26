import { useNavigate } from 'react-router-dom'
import { HiArrowLeft, HiOutlineUserPlus } from 'react-icons/hi2'
import PageContainer from '../components/PageContainer.jsx'
import TimelineStep from '../components/TimelineStep.jsx'
import StatusBadge from '../components/StatusBadge.jsx'

const STEPS = [
  {
    title: 'Intent Detected',
    description: 'Customer message classified as a billing dispute — duplicate charge.',
    timestamp: '10:42:03 AM',
  },
  {
    title: 'Customer Verified',
    description: 'Identity confirmed via secure session token and account match.',
    timestamp: '10:42:05 AM',
  },
  {
    title: 'Eligibility Checked',
    description: 'Refund policy rules applied against account transaction history.',
    timestamp: '10:42:08 AM',
  },
  {
    title: 'Duplicate Charge Confirmed',
    description: 'Two identical ₹500 annual fee charges found within the same billing cycle.',
    timestamp: '10:42:11 AM',
  },
  {
    title: 'Refund API Executed',
    description: 'Reversal of ₹500 processed through the core banking ledger.',
    timestamp: '10:42:14 AM',
  },
  {
    title: 'Customer Notified',
    description: 'Confirmation message and receipt delivered to the customer.',
    timestamp: '10:42:15 AM',
  },
]

export default function AuditPage() {
  const navigate = useNavigate()

  return (
    <PageContainer className="max-w-2xl">
      <button
        onClick={() => navigate('/confirmation')}
        className="mb-6 inline-flex items-center gap-1.5 text-sm font-medium text-ink-500 dark:text-night-300 hover:text-primary-700 dark:hover:text-primary-300 transition-colors"
      >
        <HiArrowLeft className="h-4 w-4" />
        Back to confirmation
      </button>

      <div className="mb-6 flex items-start justify-between gap-3">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-ink-900 dark:text-white tracking-tight">
            Audit trail
          </h1>
          <p className="mt-1 text-sm text-ink-500 dark:text-night-300">
            Full record of automated actions for REQ928123
          </p>
        </div>
        <StatusBadge label="6 of 6 verified" variant="success" />
      </div>

      <div className="card px-6 py-7">
        {STEPS.map((step, i) => (
          <TimelineStep
            key={step.title}
            title={step.title}
            description={step.description}
            timestamp={step.timestamp}
            isLast={i === STEPS.length - 1}
            delay={i * 90}
          />
        ))}
      </div>

      <div className="mt-6 flex flex-col sm:flex-row items-center justify-between gap-4 rounded-3xl border border-white/60 dark:border-white/10 bg-white/70 dark:bg-white/[0.04] backdrop-blur-xl px-6 py-5 shadow-glass dark:shadow-glass-dark">
        <p className="text-sm text-ink-500 dark:text-night-300 text-center sm:text-left">
          Not satisfied with this resolution? You can escalate to a live banking specialist.
        </p>
        <button onClick={() => navigate('/escalation')} className="btn-secondary shrink-0 w-full sm:w-auto">
          <HiOutlineUserPlus className="h-4 w-4" />
          Escalate to Human Agent
        </button>
      </div>
    </PageContainer>
  )
}
