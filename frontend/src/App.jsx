import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Navbar from './components/Navbar'
import AlertCenter from './components/AlertCenter'
import Dashboard from './pages/Dashboard'
import LiveMonitor from './pages/LiveMonitor'
import Reports from './pages/Reports'
import AdvancedAnalytics from './pages/AdvancedAnalytics'
import EmployeeTracker from './pages/EmployeeTracker'
import ICUGate from './pages/ICUGate'
import Alerts from './pages/Alerts'
import MLMetrics from './pages/MLMetrics'

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
            <Route path="/employees" element={<EmployeeTracker />} />
            <Route path="/employee-tracker" element={<EmployeeTracker />} />
            <Route path="/access" element={<ICUGate />} />
            <Route path="/icu-gate" element={<ICUGate />} />
            <Route path="/alerts" element={<Alerts />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/analytics" element={<AdvancedAnalytics />} />
            <Route path="/ml-metrics" element={<MLMetrics />} />
            <Route path="/ai" element={<MLMetrics />} />
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
