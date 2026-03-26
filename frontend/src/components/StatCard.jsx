import React from 'react'

export default function StatCard({ title, value, icon, color = 'blue', trend = null }) {
  const colorClasses = {
    blue: 'bg-blue-50 border-l-4 border-blue-500',
    green: 'bg-green-50 border-l-4 border-green-500',
    red: 'bg-red-50 border-l-4 border-red-500',
    yellow: 'bg-yellow-50 border-l-4 border-yellow-500',
  }

  const textColorClasses = {
    blue: 'text-blue-600',
    green: 'text-green-600',
    red: 'text-red-600',
    yellow: 'text-yellow-600',
  }

  return (
    <div className={`${colorClasses[color]} rounded-lg p-6 shadow-md hover:shadow-lg transition`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-600 text-sm font-medium">{title}</p>
          <p className={`text-3xl font-bold mt-2 ${textColorClasses[color]}`}>
            {typeof value === 'number' ? value.toFixed(1) : value}
          </p>
          {trend && (
            <p className={`text-sm mt-2 ${trend > 0 ? 'text-green-600' : 'text-red-600'}`}>
              {trend > 0 ? '📈' : '📉'} {Math.abs(trend)}% vs last week
            </p>
          )}
        </div>
        <div className={`text-4xl ${textColorClasses[color]}`}>
          {icon}
        </div>
      </div>
    </div>
  )
}
