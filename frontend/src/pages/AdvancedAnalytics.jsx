import React, { useState, useEffect } from 'react'
import { hygieneService } from '../services/api'

export default function AdvancedAnalytics() {
  const [analytics, setAnalytics] = useState(null)
  const [loading, setLoading] = useState(true)
  const [days, setDays] = useState(30)

  useEffect(() => {
    fetchAnalytics()
  }, [days])

  const fetchAnalytics = async () => {
    try {
      setLoading(true)
      const response = await fetch(`http://localhost:5000/api/analytics/dashboard?days=${days}`)
      const data = await response.json()
      setAnalytics(data.data)
    } catch (err) {
      console.error('Failed to fetch analytics:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="flex justify-center items-center h-64">
      <div className="text-gray-600">Loading analytics...</div>
    </div>
  }

  if (!analytics) {
    return <div className="bg-red-50 p-4 rounded-lg text-red-600">
      Failed to load analytics
    </div>
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-800">Advanced Analytics</h2>
          <p className="text-gray-600 mt-2">Deep insights and predictive analysis</p>
        </div>

        {/* Time Range Selector */}
        <div className="bg-white rounded-lg shadow-md p-4 mb-8">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Analysis Period
          </label>
          <select
            value={days}
            onChange={(e) => setDays(parseInt(e.target.value))}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value={7}>Last 7 Days</option>
            <option value={14}>Last 14 Days</option>
            <option value={30}>Last 30 Days</option>
            <option value={90}>Last 90 Days</option>
          </select>
        </div>

        {/* Insights Section */}
        {analytics.insights && analytics.insights.length > 0 && (
          <div className="mb-8">
            <h3 className="text-2xl font-bold text-gray-800 mb-4">🎯 Key Insights</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {analytics.insights.map((insight, idx) => (
                <div
                  key={idx}
                  className={`p-4 rounded-lg border-l-4 ${
                    insight.type === 'positive'
                      ? 'bg-green-50 border-green-500'
                      : insight.type === 'warning'
                      ? 'bg-yellow-50 border-yellow-500'
                      : 'bg-blue-50 border-blue-500'
                  }`}
                >
                  <h4 className="font-bold text-gray-800 mb-1">{insight.title}</h4>
                  <p className="text-sm text-gray-600">{insight.description}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Department Rankings */}
        {analytics.departments && (
          <div className="mb-8 bg-white rounded-lg shadow-md p-6">
            <h3 className="text-2xl font-bold text-gray-800 mb-4">🏢 Department Performance</h3>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="px-4 py-3 text-left text-sm font-semibold">Rank</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold">Department</th>
                    <th className="px-4 py-3 text-right text-sm font-semibold">Events</th>
                    <th className="px-4 py-3 text-right text-sm font-semibold">Compliant</th>
                    <th className="px-4 py-3 text-right text-sm font-semibold">Rate</th>
                    <th className="px-4 py-3 text-right text-sm font-semibold">Avg Duration</th>
                  </tr>
                </thead>
                <tbody>
                  {analytics.departments.departments.map((dept, idx) => (
                    <tr key={idx} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                      <td className="px-4 py-3">
                        <span className="inline-block w-8 h-8 bg-blue-600 text-white rounded-full text-center font-bold text-sm">
                          {dept.rank}
                        </span>
                      </td>
                      <td className="px-4 py-3 font-medium text-gray-800">{dept.department}</td>
                      <td className="px-4 py-3 text-right text-gray-600">{dept.total_events}</td>
                      <td className="px-4 py-3 text-right text-green-600 font-semibold">{dept.compliant_events}</td>
                      <td className="px-4 py-3 text-right">
                        <span className={`inline-block px-3 py-1 rounded-full text-sm font-semibold ${
                          dept.compliance_rate >= 80 ? 'bg-green-100 text-green-800' :
                          dept.compliance_rate >= 60 ? 'bg-yellow-100 text-yellow-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {dept.compliance_rate.toFixed(1)}%
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right text-gray-600">{dept.avg_duration}s</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* User Leaderboard */}
        {analytics.leaderboard && (
          <div className="mb-8 bg-white rounded-lg shadow-md p-6">
            <h3 className="text-2xl font-bold text-gray-800 mb-4">🏆 Top Performers</h3>
            <div className="space-y-3">
              {analytics.leaderboard.leaderboard.map((user, idx) => (
                <div key={idx} className="flex items-center justify-between p-4 bg-gradient-to-r from-blue-50 to-transparent rounded-lg">
                  <div className="flex items-center space-x-4">
                    <div className="text-3xl font-bold text-blue-600">#{user.rank}</div>
                    <div>
                      <p className="font-semibold text-gray-800">{user.user_id}</p>
                      <p className="text-sm text-gray-600">{user.total_events} events • {user.compliant_events} compliant</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-green-600">{user.score.toFixed(1)}</p>
                    <p className="text-xs text-gray-600">{user.compliance_rate.toFixed(1)}% compliance</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Peak Hours */}
        {analytics.peak_hours && (
          <div className="mb-8 bg-white rounded-lg shadow-md p-6">
            <h3 className="text-2xl font-bold text-gray-800 mb-4">⏰ Peak Activity Hours</h3>
            {analytics.peak_hours.peak_hour && (
              <div className="mb-4 p-4 bg-blue-50 rounded-lg border-l-4 border-blue-500">
                <p className="font-semibold text-gray-800">
                  Peak Activity: {String(analytics.peak_hours.peak_hour.hour).padStart(2, '0')}:00
                </p>
                <p className="text-sm text-gray-600">
                  {analytics.peak_hours.peak_hour.events} events with {analytics.peak_hours.peak_hour.compliance_rate.toFixed(1)}% compliance
                </p>
              </div>
            )}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              {analytics.peak_hours.hourly_breakdown && analytics.peak_hours.hourly_breakdown.slice(0, 8).map((hour, idx) => (
                <div key={idx} className="bg-gray-50 p-3 rounded-lg text-center">
                  <p className="font-bold text-gray-800">{String(hour.hour).padStart(2, '0')}:00</p>
                  <p className="text-sm text-gray-600">{hour.events} events</p>
                  <p className="text-xs text-green-600 font-semibold">{hour.compliance_rate.toFixed(1)}%</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Anomalies */}
        {analytics.anomalies && analytics.anomalies.anomalies.length > 0 && (
          <div className="mb-8 bg-red-50 rounded-lg shadow-md p-6 border-l-4 border-red-500">
            <h3 className="text-2xl font-bold text-red-800 mb-4">🚨 Detected Anomalies</h3>
            <div className="space-y-3">
              {analytics.anomalies.anomalies.slice(0, 5).map((anomaly, idx) => (
                <div key={idx} className="bg-white p-3 rounded-lg flex justify-between items-center">
                  <div>
                    <p className="font-semibold text-gray-800">{anomaly.date}</p>
                    <p className="text-sm text-gray-600">
                      {anomaly.type === 'low' ? '⬇️ Low' : '⬆️ High'} compliance at {anomaly.compliance_rate.toFixed(1)}%
                    </p>
                  </div>
                  <p className="text-sm font-bold text-red-600">σ {anomaly.z_score}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Trend Prediction */}
        {analytics.trend && (
          <div className="mb-8 bg-white rounded-lg shadow-md p-6">
            <h3 className="text-2xl font-bold text-gray-800 mb-4">📊 Compliance Trend</h3>
            <div className="grid grid-cols-3 gap-4 mb-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <p className="text-gray-600 text-sm">Trend Direction</p>
                <p className="text-2xl font-bold text-blue-600">
                  {analytics.trend.trend_direction === 'improving' ? '📈 Improving' : '📉 Declining'}
                </p>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <p className="text-gray-600 text-sm">Slope</p>
                <p className="text-2xl font-bold text-green-600">{analytics.trend.slope.toFixed(2)}%/day</p>
              </div>
              <div className="bg-purple-50 p-4 rounded-lg">
                <p className="text-gray-600 text-sm">Model Accuracy</p>
                <p className="text-2xl font-bold text-purple-600">{(analytics.trend.r_squared * 100).toFixed(1)}%</p>
              </div>
            </div>
          </div>
        )}

        {/* Export Button */}
        <div className="flex justify-center">
          <button
            onClick={() => window.open(`http://localhost:5000/api/analytics/export/csv?days=${days}`)}
            className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg transition flex items-center space-x-2"
          >
            <span>📥</span>
            <span>Download Analytics Report (CSV)</span>
          </button>
        </div>
      </div>
    </div>
  )
}
