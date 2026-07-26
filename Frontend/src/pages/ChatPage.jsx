import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { HiArrowDownTray, HiDocumentMagnifyingGlass, HiPaperAirplane } from 'react-icons/hi2'
import PageContainer from '../components/PageContainer.jsx'
import ChatBubble from '../components/ChatBubble.jsx'
import StatusBadge from '../components/StatusBadge.jsx'

export default function ChatPage() {
  const navigate = useNavigate()
  const [downloaded, setDownloaded] = useState(false)

  const handleDownload = () => {
    const receipt = [
      'ResolveAI — Confirmation Receipt',
      '--------------------------------',
      'Request ID: REQ928123',
      'Amount Reversed: ₹500',
      'Reason: Duplicate Annual Fee',
      'Status: Completed',
      '',
      'This action has been securely recorded in the audit trail.',
    ].join('\n')

    const blob = new Blob([receipt], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'ResolveAI-Confirmation-REQ928123.txt'
    link.click()
    URL.revokeObjectURL(url)

    setDownloaded(true)
    setTimeout(() => setDownloaded(false), 2000)
  }

  return (
    <PageContainer className="max-w-3xl">
      <div className="mb-6 flex items-start justify-between gap-3">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-ink-900 dark:text-white tracking-tight">
            Support conversation
          </h1>
          <p className="mt-1 text-sm text-ink-500 dark:text-night-300">
            Case reference REQ928123 &middot; Annual fee dispute
          </p>
        </div>
        <StatusBadge label="Resolved" variant="success" />
      </div>

      <div className="card overflow-hidden">
        {/* Chat window header */}
        <div className="flex items-center justify-between border-b border-white/50 dark:border-white/10 bg-white/40 dark:bg-white/[0.02] px-5 py-3.5">
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-success-500" />
            <p className="text-sm font-semibold text-ink-800 dark:text-ink-100">ResolveAI Assistant</p>
          </div>
          <p className="text-xs text-ink-400 dark:text-night-300">Today, 10:42 AM</p>
        </div>

        {/* Messages */}
        <div className="space-y-4 px-4 sm:px-6 py-6 min-h-[320px]">
          <ChatBubble from="customer" delay={0}>
            I was charged my annual fee twice.
          </ChatBubble>

          <ChatBubble from="ai" delay={150}>
            I checked your account and found two annual fee charges. The duplicate charge is
            eligible for reversal.
          </ChatBubble>

          <ChatBubble from="ai" delay={350} emphasis>
            ₹500 has been successfully reversed.
          </ChatBubble>

          {/* Action buttons attached to the resolution message */}
          <div className="flex flex-wrap gap-3 pt-1 pl-9 animate-fadeUp" style={{ animationDelay: '500ms' }}>
            <button onClick={() => navigate('/confirmation')} className="btn-primary">
              <HiDocumentMagnifyingGlass className="h-4 w-4" />
              View Details
            </button>
            <button onClick={handleDownload} className="btn-secondary">
              <HiArrowDownTray className="h-4 w-4" />
              {downloaded ? 'Downloaded' : 'Download Confirmation'}
            </button>
          </div>
        </div>

        {/* Disabled composer for realism */}
        <div className="border-t border-white/50 dark:border-white/10 px-4 sm:px-6 py-4">
          <div className="flex items-center gap-3 rounded-full border border-white/50 dark:border-white/10 bg-white/40 dark:bg-white/[0.03] px-4 py-3">
            <input
              disabled
              placeholder="This conversation has been resolved"
              className="flex-1 bg-transparent text-sm text-ink-400 dark:text-night-300 placeholder:text-ink-400 dark:placeholder:text-night-500 outline-none cursor-not-allowed"
            />
            <button
              disabled
              className="flex h-8 w-8 items-center justify-center rounded-full bg-ink-200 dark:bg-white/10 text-ink-400 dark:text-night-300 cursor-not-allowed"
            >
              <HiPaperAirplane className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      <p className="mt-4 text-center text-xs text-ink-400 dark:text-night-300">
        Protected by 256-bit encryption &middot; ResolveAI never shares your data without consent
      </p>
    </PageContainer>
  )
}
