import React from 'react'

export default function Navbar() {
  return (
    <nav className="bg-gradient-to-r from-blue-600 to-blue-800 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="text-2xl font-bold">🏥</div>
            <div>
              <h1 className="text-xl font-bold">Hand Hygiene Monitor</h1>
              <p className="text-blue-100 text-sm">AI-Powered Compliance System</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-6">
            <div className="flex space-x-4">
              <a href="/" className="hover:bg-blue-700 px-3 py-2 rounded-lg transition">
                Dashboard
              </a>
              <a href="/monitor" className="hover:bg-blue-700 px-3 py-2 rounded-lg transition">
                Live Monitor
              </a>
              <a href="/reports" className="hover:bg-blue-700 px-3 py-2 rounded-lg transition">
                Reports
              </a>
              <a href="/analytics" className="hover:bg-blue-700 px-3 py-2 rounded-lg transition">
                Analytics
              </a>
            </div>
            
            <div className="w-10 h-10 bg-blue-700 rounded-full flex items-center justify-center">
              <span className="text-sm font-bold">👤</span>
            </div>
          </div>
        </div>
      </div>
    </nav>
  )
}
