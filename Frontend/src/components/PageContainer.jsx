export default function PageContainer({ children, className = '' }) {
  return (
    <div className={`max-w-5xl mx-auto px-4 sm:px-6 py-8 sm:py-12 ${className}`}>
      {children}
    </div>
  )
}
