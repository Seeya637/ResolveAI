export default function SuccessSeal() {
  return (
    <div className="relative flex h-20 w-20 items-center justify-center">
      <span className="absolute inset-0 rounded-full bg-success-500/30 animate-pulseRing" />
      <span className="absolute inset-0 rounded-full bg-success-500/20 animate-pulseRing [animation-delay:0.4s]" />
      <span className="relative flex h-20 w-20 items-center justify-center rounded-full bg-gradient-to-br from-success-500 to-success-700 shadow-pop animate-popIn">
        <svg viewBox="0 0 24 24" className="h-9 w-9" fill="none">
          <path
            d="M5 12.5 10 17.5 19 7"
            stroke="white"
            strokeWidth="2.4"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeDasharray="24"
            strokeDashoffset="24"
            className="animate-drawCheck"
          />
        </svg>
      </span>
    </div>
  )
}
