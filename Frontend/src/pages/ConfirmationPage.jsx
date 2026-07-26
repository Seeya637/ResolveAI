import { useNavigate } from 'react-router-dom'
import { HiArrowLeft, HiLockClosed, HiOutlineClipboardDocumentList } from 'react-icons/hi2'
import PageContainer from '../components/PageContainer.jsx'
import InfoRow from '../components/InfoRow.jsx'
import SuccessSeal from '../components/SuccessSeal.jsx'
import StatusBadge from '../components/StatusBadge.jsx'

export default function ConfirmationPage() {
  const navigate = useNavigate()

  return (
    <PageContainer className="max-w-md">
      <button
        onClick={() => navigate('/')}
        className="mb-6 inline-flex items-center gap-1.5 text-sm font-medium text-ink-500 dark:text-night-300 hover:text-primary-700 dark:hover:text-primary-300 transition-colors"
      >
        <HiArrowLeft className="h-4 w-4" />
        Back to chat
      </button>

      <div className="card overflow-hidden">
        {/* Receipt header */}
        <div className="flex flex-col items-center gap-4 border-b border-dashed border-ink-200 dark:border-white/10 px-6 pt-8 pb-7 text-center">
          <SuccessSeal />
          <div>
            <h1 className="text-lg font-bold text-ink-900 dark:text-white">Reversal completed</h1>
            <p className="mt-1 text-sm text-ink-500 dark:text-night-300">
              Your duplicate charge has been refunded to your account.
            </p>
          </div>
          <StatusBadge label="Status: Completed" variant="success" />
        </div>

        {/* Receipt body */}
        <div className="px-6 py-2 divide-y divide-ink-100 dark:divide-white/10">
          <InfoRow label="Request ID" value="REQ928123" mono />
          <InfoRow label="Amount Reversed" value="₹500" highlight />
          <InfoRow label="Reason" value="Duplicate Annual Fee" />
          <InfoRow label="Status" value="Completed" />
        </div>

        {/* Notice */}
        <div className="mx-6 mb-6 mt-4 flex items-start gap-3 rounded-2xl bg-primary-50/80 dark:bg-primary-500/10 border border-primary-100 dark:border-primary-500/20 px-4 py-3.5 backdrop-blur-sm">
          <HiLockClosed className="h-4.5 w-4.5 mt-0.5 shrink-0 text-primary-600 dark:text-primary-300" />
          <p className="text-xs leading-relaxed text-primary-800 dark:text-primary-200">
            This action has been securely recorded in the audit trail.
          </p>
        </div>

        <div className="px-6 pb-6">
          <button onClick={() => navigate('/audit')} className="btn-primary w-full">
            <HiOutlineClipboardDocumentList className="h-4 w-4" />
            View Audit Trail
          </button>
        </div>
      </div>
    </PageContainer>
  )
}
