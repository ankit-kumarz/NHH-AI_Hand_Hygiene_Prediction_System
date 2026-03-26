import React, { useState, useEffect } from 'react'

export default function AlertNotification({ message, type = 'info', duration = 5000, onClose = null }) {
  const [isVisible, setIsVisible] = useState(true)

  useEffect(() => {
    if (duration) {
      const timer = setTimeout(() => {
        setIsVisible(false)
        if (onClose) onClose()
      }, duration)
      return () => clearTimeout(timer)
    }
  }, [duration, onClose])

  if (!isVisible) return null

  const typeStyles = {
    success: 'bg-green-500 border-l-4 border-green-600',
    warning: 'bg-yellow-500 border-l-4 border-yellow-600',
    error: 'bg-red-500 border-l-4 border-red-600',
    info: 'bg-blue-500 border-l-4 border-blue-600',
  }

  const typeIcons = {
    success: '✅',
    warning: '⚠️',
    error: '❌',
    info: 'ℹ️',
  }

  return (
    <div className={`${typeStyles[type]} text-white p-4 rounded shadow-lg animate-slide-in`}>
      <div className="flex items-center space-x-3">
        <span className="text-2xl">{typeIcons[type]}</span>
        <p className="text-sm font-medium">{message}</p>
        <button
          onClick={() => setIsVisible(false)}
          className="ml-auto text-white hover:opacity-75"
        >
          ✕
        </button>
      </div>
    </div>
  )
}
