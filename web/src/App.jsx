import React, { useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AnimatePresence } from 'framer-motion'
import { useAuthStore } from './store/auth'

import LandingPage from './pages/Landing'
import AuthPage from './pages/Auth'
import Dashboard from './pages/Dashboard'
import OnboardingPage from './pages/Onboarding'
import EventsPage from './pages/Events'
import ConversationPage from './pages/Conversation'
import FutureSelfPage from './pages/FutureSelf'
import ExportPage from './pages/Export'

export default function App() {
  const { token, loadToken } = useAuthStore()

  useEffect(() => {
    loadToken()
  }, [])

  return (
    <BrowserRouter>
      <AnimatePresence mode="wait">
        <Routes>
          <Route path="/" element={token ? <Navigate to="/dashboard" /> : <LandingPage />} />
          <Route path="/auth" element={token ? <Navigate to="/dashboard" /> : <AuthPage />} />

          {token ? (
            <>
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/onboarding" element={<OnboardingPage />} />
              <Route path="/events" element={<EventsPage />} />
              <Route path="/conversation" element={<ConversationPage />} />
              <Route path="/future-self" element={<FutureSelfPage />} />
              <Route path="/export" element={<ExportPage />} />
            </>
          ) : (
            <Route path="*" element={<Navigate to="/" />} />
          )}
        </Routes>
      </AnimatePresence>
    </BrowserRouter>
  )
}
