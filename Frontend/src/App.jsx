import { Routes, Route, useLocation } from 'react-router-dom'
import Header from './components/Header.jsx'
import GradientBackdrop from './components/GradientBackdrop.jsx'
import ChatPage from './pages/ChatPage.jsx'
import ConfirmationPage from './pages/ConfirmationPage.jsx'
import AuditPage from './pages/AuditPage.jsx'
import EscalationPage from './pages/EscalationPage.jsx'

export default function App() {
  const location = useLocation()

  return (
    <div className="min-h-screen flex flex-col">
      <GradientBackdrop />
      <Header />
      <main key={location.pathname} className="flex-1 page-enter">
        <Routes location={location}>
          <Route path="/" element={<ChatPage />} />
          <Route path="/confirmation" element={<ConfirmationPage />} />
          <Route path="/audit" element={<AuditPage />} />
          <Route path="/escalation" element={<EscalationPage />} />
        </Routes>
      </main>
    </div>
  )
}
