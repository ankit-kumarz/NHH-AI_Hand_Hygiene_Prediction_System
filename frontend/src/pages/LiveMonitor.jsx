import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { Camera, Users, AlertCircle, CheckCircle } from 'lucide-react'

const API_BASE = 'http://localhost:5000/api'

export default function LiveMonitor() {
  const [employees, setEmployees] = useState([])
  const [selectedEmployee, setSelectedEmployee] = useState('')
  const [status, setStatus] = useState('Idle')
  const [progress, setProgress] = useState(0)
  const [timer, setTimer] = useState(0)
  const [connected, setConnected] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [cameraStarted, setCameraStarted] = useState(false)

  // Load employees and check connection
  useEffect(() => {
    const initializeApp = async () => {
      try {
        setError(null)
        
        // Check backend connection
        try {
          const healthResponse = await axios.get(`${API_BASE}/health`)
          setConnected(true)
        } catch (err) {
          setError('❌ Cannot connect to backend (http://localhost:5000)')
          setConnected(false)
          setLoading(false)
          return
        }

        // Load employees
        try {
          const employeeResponse = await axios.get(`${API_BASE}/employees`)
          if (employeeResponse.data.success) {
            setEmployees(employeeResponse.data.employees)
            if (employeeResponse.data.employees.length === 0) {
              setError('⚠️ No employees in database. Run: python scripts/populate_mock_data.py')
            }
          }
        } catch (err) {
          setError('❌ Failed to load employees from API')
        }
      } finally {
        setLoading(false)
      }
    }

    initializeApp()

    // Simulate real-time updates (will be replaced with WebSocket in Phase 4)
    const interval = setInterval(() => {
      if (cameraStarted) {
        simulateDetection()
      }
    }, 2000)

    return () => clearInterval(interval)
  }, [cameraStarted])

  const startCamera = () => {
    if (!selectedEmployee) {
      setError('❌ Please select an employee first')
      return
    }
    setCameraStarted(true)
    setError(null)
    setStatus('Detected')
  }

  const stopCamera = () => {
    setCameraStarted(false)
    setStatus('Idle')
    setTimer(0)
    setProgress(0)
  }

  const simulateDetection = () => {
    // Simulate hand detection
    const statuses = ['Detected', 'Washing', 'Completed']
    const randomStatus = statuses[Math.floor(Math.random() * statuses.length)]
    setStatus(randomStatus)
    
    if (randomStatus === 'Washing') {
      setTimer(prev => (prev < 20 ? prev + 0.5 : 20))
      setProgress(Math.min((timer / 20) * 100, 100))
    } else if (randomStatus === 'Completed') {
      setProgress(100)
      setTimer(20)
      // Auto-log this wash event
      if (selectedEmployee) {
        logWashEvent()
      }
    }
  }

  const logWashEvent = async () => {
    try {
      const now = new Date()
      await axios.post(`${API_BASE}/wash-event`, {
        employee_id: selectedEmployee,
        start_time: new Date(now.getTime() - 20000).toISOString(),
        end_time: now.toISOString(),
        duration: timer,
        compliant: timer >= 20,
        hand_movement_score: 0.85
      })
    } catch (err) {
      console.error('Failed to log wash event:', err)
    }
  }

  const getStatusColor = () => {
    switch (status) {
      case 'Completed':
        return 'bg-green-500'
      case 'Washing':
        return 'bg-blue-500'
      case 'Detected':
        return 'bg-yellow-500'
      default:
        return 'bg-gray-500'
    }
  }

  const getStatusIcon = () => {
    switch (status) {
      case 'Completed':
        return '✅'
      case 'Washing':
        return '🧼'
      case 'Detected':
        return '👋'
      default:
        return '⏸️'
    }
  }

  const selectedEmployeeData = employees.find(e => e.employee_id === selectedEmployee)

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-blue-700 p-8 flex items-center justify-center">
        <div className="text-center text-white">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-white mb-4"></div>
          <p>Initializing system...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-blue-700 p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-2">
            <Camera className="w-8 h-8 text-white" />
            <h1 className="text-3xl font-bold text-white">Live Monitor</h1>
          </div>
          <p className="text-blue-100">Real-time hand hygiene detection</p>
          <p className={`text-sm mt-2 ${connected ? 'text-green-300' : 'text-red-300'}`}>
            {connected ? '🟢 Connected to Backend' : '🔴 Backend Offline'}
          </p>
        </div>

        {/* Error Messages */}
        {error && (
          <div className="mb-6 bg-red-900 border border-red-500 text-red-100 px-4 py-3 rounded-lg flex items-start gap-3">
            <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold">Error</p>
              <p className="text-sm mt-1">{error}</p>
            </div>
          </div>
        )}

        {/* Employee Selection Card */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <Users className="w-5 h-5 text-blue-600" />
            <h2 className="text-xl font-bold text-gray-800">Select Employee</h2>
          </div>

          <select
            value={selectedEmployee}
            onChange={(e) => {
              setSelectedEmployee(e.target.value)
              setCameraStarted(false)
              setStatus('Idle')
              setError(null)
            }}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 mb-4"
          >
            <option value="">-- Select an employee to start --</option>
            {employees.map(emp => (
              <option key={emp.employee_id} value={emp.employee_id}>
                {emp.name} - {emp.department} ({emp.role})
              </option>
            ))}
          </select>

          {/* Selected Employee Info */}
          {selectedEmployeeData && (
            <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-gray-600 text-sm">Current Employee</p>
                  <p className="text-lg font-bold text-gray-800">{selectedEmployeeData.name}</p>
                  <p className="text-gray-600 text-sm mt-1">
                    {selectedEmployeeData.department} • {selectedEmployeeData.role}
                  </p>
                  <p className="text-gray-700 font-semibold mt-2">
                    Compliance Rate: 
                    <span className={`ml-2 ${
                      selectedEmployeeData.compliance_rate >= 85 ? 'text-green-600' :
                      selectedEmployeeData.compliance_rate >= 70 ? 'text-yellow-600' :
                      'text-red-600'
                    }`}>
                      {(selectedEmployeeData.compliance_rate || 0).toFixed(1)}%
                    </span>
                  </p>
                </div>
                {selectedEmployeeData.last_wash_time && (
                  <div className="text-right text-sm text-gray-600">
                    <p>Last Wash: {new Date(selectedEmployeeData.last_wash_time).toLocaleTimeString()}</p>
                    <span className={`inline-block mt-1 px-2 py-1 rounded text-white text-xs font-bold ${
                      selectedEmployeeData.last_wash_compliant ? 'bg-green-600' : 'bg-red-600'
                    }`}>
                      {selectedEmployeeData.last_wash_compliant ? '✓ Compliant' : '✗ Incomplete'}
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Camera Status Card */}
        {selectedEmployee ? (
          <div className="bg-white rounded-lg shadow-lg overflow-hidden">
            {/* Camera Display */}
            <div className={`${getStatusColor()} transition-colors duration-300 p-12 text-center text-white`}>
              <div className="text-6xl mb-4">{getStatusIcon()}</div>
              <h3 className="text-2xl font-bold mb-2">{status}</h3>
              <p className="text-blue-100 mb-4">
                {cameraStarted ? 'Webcam is active' : 'Click Start to begin detection'}
              </p>
            </div>

            {/* Timer and Progress */}
            {cameraStarted && (
              <div className="p-6 bg-gray-50">
                <div className="mb-4">
                  <div className="flex justify-between mb-2">
                    <span className="font-semibold text-gray-700">Duration</span>
                    <span className={`text-2xl font-bold ${timer >= 20 ? 'text-green-600' : 'text-blue-600'}`}>
                      {timer.toFixed(1)}s
                    </span>
                  </div>
                  <div className="w-full bg-gray-300 rounded-full h-3 overflow-hidden">
                    <div
                      className={`h-full transition-all ${timer >= 20 ? 'bg-green-500' : 'bg-blue-500'}`}
                      style={{ width: `${progress}%` }}
                    ></div>
                  </div>
                  <p className="text-sm text-gray-600 mt-2">Target: 20 seconds (WHO Standard)</p>
                </div>

                {/* Compliance Result */}
                {status === 'Completed' && (
                  <div className={`mt-4 p-4 rounded-lg flex items-center gap-3 ${
                    timer >= 20 ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
                  }`}>
                    {timer >= 20 ? (
                      <>
                        <CheckCircle className="w-6 h-6 text-green-600" />
                        <div>
                          <p className="font-bold text-green-800">Compliant Wash</p>
                          <p className="text-sm text-green-700">{timer.toFixed(1)}s - exceeds 20s requirement</p>
                        </div>
                      </>
                    ) : (
                      <>
                        <AlertCircle className="w-6 h-6 text-red-600" />
                        <div>
                          <p className="font-bold text-red-800">Incomplete Wash</p>
                          <p className="text-sm text-red-700">{timer.toFixed(1)}s - needs at least 20s</p>
                        </div>
                      </>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Control Buttons */}
            <div className="p-6 bg-white border-t border-gray-200 flex gap-3">
              <button
                onClick={startCamera}
                disabled={!selectedEmployee || cameraStarted}
                className="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-bold py-3 px-4 rounded-lg transition"
              >
                Start Detection
              </button>
              <button
                onClick={stopCamera}
                disabled={!cameraStarted}
                className="flex-1 bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white font-bold py-3 px-4 rounded-lg transition"
              >
                Stop Detection
              </button>
            </div>
          </div>
        ) : (
          <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 px-6 py-8 rounded-lg text-center">
            <AlertCircle className="w-12 h-12 mx-auto mb-3 text-yellow-600" />
            <p className="font-semibold mb-2">Select an employee to begin</p>
            <p className="text-sm">Choose from the dropdown above to start hand hygiene detection</p>
          </div>
        )}

        {/* Connection Status */}
        <div className="mt-8 text-center">
          <div className={`inline-block px-4 py-2 rounded-lg ${
            connected ? 'bg-green-900 text-green-100' : 'bg-red-900 text-red-100'
          }`}>
            {connected ? '✅ Backend Connected' : '❌ Backend Disconnected'}
          </div>
        </div>
      </div>
    </div>
  )
}
