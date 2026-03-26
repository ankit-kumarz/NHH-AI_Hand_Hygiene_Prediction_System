import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Navbar from './components/Navbar'
import AlertCenter from './components/AlertCenter'
import Dashboard from './pages/Dashboard'
import LiveMonitor from './pages/LiveMonitor'
import Reports from './pages/Reports'
import AdvancedAnalytics from './pages/AdvancedAnalytics'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        <Navbar />
        <AlertCenter />
        <main>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/monitor" element={<LiveMonitor />} />
            <Route path="/live" element={<LiveMonitor />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/analytics" element={<AdvancedAnalytics />} />
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
