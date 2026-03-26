import React, { useState, useEffect } from 'react'
import { hygieneService } from '../services/api'

export default function LiveMonitor() {
  const [status, setStatus] = useState('Idle')
  const [progress, setProgress] = useState(0)
  const [timer, setTimer] = useState(0)
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    // Check backend connection
    checkConnection()
    
    // Simulate real-time updates
    const interval = setInterval(() => {
      checkConnection()
      simulateDetection()
    }, 2000)

    return () => clearInterval(interval)
  }, [])

  const checkConnection = async () => {
    try {
      await hygieneService.healthCheck()
      setConnected(true)
    } catch (err) {
      setConnected(false)
    }
  }

  const simulateDetection = () => {
    // This will be replaced with actual WebSocket connection in Phase 4
    const statuses = ['Idle', 'Detected', 'Washing', 'Completed']
    const randomStatus = statuses[Math.floor(Math.random() * statuses.length)]
    setStatus(randomStatus)
    
    if (randomStatus === 'Washing') {
      setTimer(prev => (prev < 20 ? prev + 0.5 : 20))
      setProgress(Math.min((timer / 20) * 100, 100))
    } else if (randomStatus === 'Completed') {
      setProgress(100)
      setTimer(20)
    } else {
      setProgress(0)
      setTimer(0)
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-blue-700 p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-white mb-2">Live Monitor</h2>
          <p className="text-blue-100">Real-time hand hygiene detection</p>
          
          {/* Connection Status */}
          <div className="mt-4 flex items-center justify-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${connected ? 'bg-green-400' : 'bg-red-400'} animate-pulse`}></div>
            <span className={`text-sm ${connected ? 'text-green-300' : 'text-red-300'}`}>
              {connected ? '🟢 Connected to Backend' : '🔴 Disconnected'}
            </span>
          </div>
        </div>

        {/* Main Status Display */}
        <div className="bg-white rounded-2xl shadow-2xl p-12 mb-8">
          <div className="text-center">
            {/* Status Icon */}
            <div className="text-8xl mb-4 animate-bounce">
              {getStatusIcon()}
            </div>

            {/* Status Text */}
            <div className={`${getStatusColor()} text-white px-8 py-3 rounded-lg inline-block mb-6`}>
              <p className="text-2xl font-bold">{status}</p>
            </div>

            {/* Timer Display */}
            <div className="my-8">
              <p className="text-gray-600 text-sm mb-2">Duration</p>
              <p className="text-6xl font-bold text-blue-600">
                {timer.toFixed(1)}s
              </p>
              <p className="text-gray-600 mt-2">Target: 20 seconds (WHO Standard)</p>
            </div>

            {/* Progress Bar */}
            <div className="my-8">
              <div className="bg-gray-200 rounded-full h-8 overflow-hidden">
                <div
                  className={`${getStatusColor()} h-full transition-all duration-300 flex items-center justify-center text-white font-bold text-sm`}
                  style={{ width: `${progress}%` }}
                >
                  {progress > 10 && `${Math.round(progress)}%`}
                </div>
              </div>
            </div>

            {/* Status Details */}
            <div className="grid grid-cols-3 gap-4 mt-8">
              <div className="bg-blue-50 p-4 rounded-lg">
                <p className="text-gray-600 text-sm">Current Time</p>
                <p className="text-xl font-bold text-blue-600">{timer.toFixed(1)}s</p>
              </div>
              <div className="bg-yellow-50 p-4 rounded-lg">
                <p className="text-gray-600 text-sm">Required Time</p>
                <p className="text-xl font-bold text-yellow-600">20s</p>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <p className="text-gray-600 text-sm">Progress</p>
                <p className="text-xl font-bold text-green-600">{Math.round(progress)}%</p>
              </div>
            </div>
          </div>
        </div>

        {/* Instructions */}
        <div className="bg-white bg-opacity-10 backdrop-blur-md text-white rounded-lg p-6 border border-white border-opacity-20">
          <h3 className="text-lg font-bold mb-3">How it works:</h3>
          <ol className="space-y-2 text-sm">
            <li className="flex items-start space-x-3">
              <span className="font-bold">1.</span>
              <span>Camera detects hands in front of the sensor</span>
            </li>
            <li className="flex items-start space-x-3">
              <span className="font-bold">2.</span>
              <span>System starts timer automatically</span>
            </li>
            <li className="flex items-start space-x-3">
              <span className="font-bold">3.</span>
              <span>Maintain handwashing for 20+ seconds</span>
            </li>
            <li className="flex items-start space-x-3">
              <span className="font-bold">4.</span>
              <span>Event automatically logged when complete</span>
            </li>
          </ol>
        </div>

        {/* Status Alerts */}
        {status === 'Completed' && (
          <div className="mt-8 bg-green-500 text-white p-6 rounded-lg animate-pulse text-center">
            <p className="text-2xl font-bold">✅ Excellent! Proper handwashing completed</p>
          </div>
        )}

        {status === 'Detected' && (
          <div className="mt-8 bg-yellow-500 text-white p-6 rounded-lg animate-pulse text-center">
            <p className="text-2xl font-bold">👋 Hands detected - Start handwashing</p>
          </div>
        )}

        {status === 'Washing' && progress > 0 && progress < 20 && (
          <div className="mt-8 bg-blue-500 text-white p-6 rounded-lg text-center">
            <p className="text-2xl font-bold">🧼 Washing in progress... ({Math.round((timer / 20) * 100)}%)</p>
          </div>
        )}
      </div>
    </div>
  )
}
