import React, { useState, useEffect } from 'react'
import { LineChart, BarChart, PieChart } from '../components/Chart'
import { hygieneService } from '../services/api'

export default function Reports() {
  const [timeRange, setTimeRange] = useState(30)
  const [userStats, setUserStats] = useState(null)
  const [dailyStats, setDailyStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [selectedUser, setSelectedUser] = useState('')

  useEffect(() => {
    fetchReportData()
  }, [timeRange, selectedUser])

  const fetchReportData = async () => {
    try {
      setLoading(true)
      const daily = await hygieneService.getDailyStats({ days: timeRange })
      setDailyStats(daily.data)

      if (selectedUser) {
        const user = await hygieneService.getUserStats(selectedUser, { days: timeRange })
        setUserStats(user.data)
      }
    } catch (err) {
      console.error('Failed to fetch reports:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="flex justify-center items-center h-64">
      <div className="text-gray-600">Loading...</div>
    </div>
  }

  const dailyData = dailyStats?.daily_stats || []

  const complianceTrendData = {
    labels: dailyData.map(d => d.date),
    datasets: [{
      label: 'Compliance Rate (%)',
      data: dailyData.map(d => d.compliance_rate),
      borderColor: '#3b82f6',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      borderWidth: 2,
      fill: true,
      tension: 0.4,
    }],
  }

  const eventsData = {
    labels: dailyData.map(d => d.date),
    datasets: [{
      label: 'Compliant Events',
      data: dailyData.map(d => d.completed_events),
      backgroundColor: '#10b981',
    }, {
      label: 'Incomplete Events',
      data: dailyData.map(d => d.incomplete_events),
      backgroundColor: '#ef4444',
    }],
  }

  const durationData = {
    labels: dailyData.map(d => d.date),
    datasets: [{
      label: 'Average Duration (seconds)',
      data: dailyData.map(d => d.avg_duration),
      borderColor: '#f59e0b',
      backgroundColor: 'rgba(245, 158, 11, 0.1)',
      borderWidth: 2,
      fill: true,
    }],
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-800">Reports & Analytics</h2>
          <p className="text-gray-600 mt-2">Detailed compliance analysis and trends</p>
        </div>

        {/* Controls */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Time Range
              </label>
              <select
                value={timeRange}
                onChange={(e) => setTimeRange(parseInt(e.target.value))}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value={7}>Last 7 Days</option>
                <option value={14}>Last 14 Days</option>
                <option value={30}>Last 30 Days</option>
                <option value={90}>Last 90 Days</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Filter by User (Optional)
              </label>
              <input
                type="text"
                placeholder="Enter User ID (e.g., USER001)"
                value={selectedUser}
                onChange={(e) => setSelectedUser(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          <LineChart
            data={complianceTrendData}
            title="Compliance Trend"
          />
          <BarChart
            data={eventsData}
            title="Events Breakdown"
          />
        </div>

        <div className="mb-8">
          <LineChart
            data={durationData}
            title="Average Wash Duration Trend"
          />
        </div>

        {/* Summary Stats */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-bold text-gray-800 mb-6">Summary Statistics</h3>
          
          {dailyData.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="border-l-4 border-blue-500 pl-4">
                <p className="text-gray-600 text-sm">Total Events (Period)</p>
                <p className="text-2xl font-bold text-blue-600">
                  {dailyData.reduce((sum, d) => sum + d.total_events, 0)}
                </p>
              </div>
              <div className="border-l-4 border-green-500 pl-4">
                <p className="text-gray-600 text-sm">Avg Compliance Rate</p>
                <p className="text-2xl font-bold text-green-600">
                  {(dailyData.reduce((sum, d) => sum + d.compliance_rate, 0) / dailyData.length).toFixed(1)}%
                </p>
              </div>
              <div className="border-l-4 border-yellow-500 pl-4">
                <p className="text-gray-600 text-sm">Avg Duration</p>
                <p className="text-2xl font-bold text-yellow-600">
                  {(dailyData.reduce((sum, d) => sum + d.avg_duration, 0) / dailyData.length).toFixed(1)}s
                </p>
              </div>
              <div className="border-l-4 border-purple-500 pl-4">
                <p className="text-gray-600 text-sm">Best Day</p>
                <p className="text-2xl font-bold text-purple-600">
                  {Math.max(...dailyData.map(d => d.compliance_rate)).toFixed(1)}%
                </p>
              </div>
            </div>
          ) : (
            <p className="text-gray-600">No data available for selected period</p>
          )}
        </div>

        {/* User Stats */}
        {selectedUser && userStats && (
          <div className="mt-8 bg-blue-50 rounded-lg shadow-md p-6 border-l-4 border-blue-500">
            <h3 className="text-xl font-bold text-gray-800 mb-4">User Statistics: {selectedUser}</h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <p className="text-gray-600 text-sm">Total Events</p>
                <p className="text-2xl font-bold text-blue-600">{userStats.total_events}</p>
              </div>
              <div>
                <p className="text-gray-600 text-sm">Compliant Events</p>
                <p className="text-2xl font-bold text-green-600">{userStats.compliant_events}</p>
              </div>
              <div>
                <p className="text-gray-600 text-sm">Compliance Rate</p>
                <p className="text-2xl font-bold text-yellow-600">{userStats.compliance_rate}%</p>
              </div>
              <div>
                <p className="text-gray-600 text-sm">Avg Duration</p>
                <p className="text-2xl font-bold text-purple-600">{userStats.avg_duration}s</p>
              </div>
            </div>
          </div>
        )}

        {/* Export Button */}
        <div className="mt-8 flex justify-center space-x-4">
          <button className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition">
            📥 Download Report
          </button>
          <button className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg transition">
            📧 Email Report
          </button>
        </div>
      </div>
    </div>
  )
}
