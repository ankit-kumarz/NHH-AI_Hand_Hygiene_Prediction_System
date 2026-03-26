import React, { useState, useEffect } from 'react'
import AlertNotification from './AlertNotification'
import socket, { socketEvents, socketEmit } from '../services/socket'

export default function AlertCenter() {
  const [alerts, setAlerts] = useState([])
  const [connectionStatus, setConnectionStatus] = useState('disconnected')

  useEffect(() => {
    // Connection events
    socketEvents.onConnect(() => {
      setConnectionStatus('connected')
      console.log('🟢 Connected to real-time server')
    })

    socketEvents.onDisconnect(() => {
      setConnectionStatus('disconnected')
      console.log('🔴 Disconnected from real-time server')
    })

    socketEvents.onConnectionResponse((data) => {
      console.log('Connection response:', data)
    })

    // Alert events
    socketEvents.onCompletionAlert((data) => {
      addAlert(data.data.message, 'success', 4000)
      console.log('✅ Completion Alert:', data)
    })

    socketEvents.onFailureAlert((data) => {
      addAlert(data.data.message, 'warning', 4000)
      console.log('⚠️ Failure Alert:', data)
    })

    socketEvents.onDetectionEvent((data) => {
      console.log('👋 Detection Event:', data)
    })

    socketEvents.onStatusUpdate((data) => {
      console.log('📊 Status Update:', data)
    })

    socketEvents.onSystemAlert((data) => {
      addAlert(data.message, data.type, 5000)
      console.log('🔔 System Alert:', data)
    })

    // Cleanup
    return () => {
      socket.off('connect')
      socket.off('disconnect')
      socket.off('completion_alert')
      socket.off('failure_alert')
      socket.off('system_alert')
    }
  }, [])

  const addAlert = (message, type = 'info', duration = 5000) => {
    const id = Date.now()
    setAlerts((prev) => [...prev, { id, message, type, duration }])
  }

  const removeAlert = (id) => {
    setAlerts((prev) => prev.filter((alert) => alert.id !== id))
  }

  return (
    <div className="fixed top-4 right-4 z-50 space-y-3 max-w-md">
      {/* Connection Status Indicator */}
      <div className="flex items-center justify-end space-x-2 text-xs font-medium">
        <span className={`w-2 h-2 rounded-full ${connectionStatus === 'connected' ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></span>
        <span className={connectionStatus === 'connected' ? 'text-green-600' : 'text-red-600'}>
          {connectionStatus === 'connected' ? '🟢 Live' : '🔴 Offline'}
        </span>
      </div>

      {/* Alerts */}
      {alerts.map((alert) => (
        <AlertNotification
          key={alert.id}
          message={alert.message}
          type={alert.type}
          duration={alert.duration}
          onClose={() => removeAlert(alert.id)}
        />
      ))}
    </div>
  )
}
