import React, { useState, useEffect } from 'react'
import { Bell } from 'lucide-react'
import axios from 'axios'

const API_BASE = 'http://localhost:5000/api'

export default function Navbar() {
  const [alertCount, setAlertCount] = useState(0)

  // Fetch alert count
  useEffect(() => {
    const fetchAlertCount = async () => {
      try {
        const response = await axios.get(`${API_BASE}/alerts/unacknowledged`)
        if (response.data.success) {
          setAlertCount(response.data.count)
        }
      } catch (err) {
        console.error('Failed to fetch alert count:', err)
      }
    }

    fetchAlertCount()
    // Refresh every 30 seconds
    const interval = setInterval(fetchAlertCount, 30000)
    return () => clearInterval(interval)
  }, [])

  return (
    <nav className="bg-gradient-to-r from-blue-600 to-blue-800 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="text-2xl font-bold">🏥</div>
            <div>
              <h1 className="text-xl font-bold">Hand Hygiene Monitor</h1>
              <p className="text-blue-100 text-sm">Complete Employee Tracking System</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-6">
            <div className="flex space-x-1">
              <a href="/" className="hover:bg-blue-700 px-3 py-2 rounded-lg transition text-sm">
                Dashboard
              </a>
              <a href="/monitor" className="hover:bg-blue-700 px-3 py-2 rounded-lg transition text-sm">
                Monitor
              </a>
              <a href="/employees" className="hover:bg-blue-700 px-3 py-2 rounded-lg transition text-sm">
                Employees
              </a>
              <a href="/access" className="hover:bg-blue-700 px-3 py-2 rounded-lg transition text-sm">
                ICU Gate
              </a>
              <a href="/reports" className="hover:bg-blue-700 px-3 py-2 rounded-lg transition text-sm">
                Reports
              </a>
              <a href="/analytics" className="hover:bg-blue-700 px-3 py-2 rounded-lg transition text-sm">
                Analytics
              </a>
              <a href="/ml-metrics" className="hover:bg-blue-700 px-3 py-2 rounded-lg transition text-sm">
                🤖 AI Model
              </a>
            </div>

            {/* Alerts Button */}
            <a href="/alerts" className="relative hover:bg-blue-700 px-3 py-2 rounded-lg transition flex items-center gap-2">
              <Bell className="w-5 h-5" />
              <span className="text-sm">Alerts</span>
              {alertCount > 0 && (
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs font-bold rounded-full h-6 w-6 flex items-center justify-center">
                  {alertCount > 9 ? '9+' : alertCount}
                </span>
              )}
            </a>
            
            <div className="w-10 h-10 bg-blue-700 rounded-full flex items-center justify-center">
              <span className="text-sm font-bold">👤</span>
            </div>
          </div>
        </div>
      </div>
    </nav>
  )
}
