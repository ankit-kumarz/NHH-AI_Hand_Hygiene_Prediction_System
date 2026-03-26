import React, { useState, useEffect } from 'react'
import StatCard from '../components/StatCard'
import { LineChart, PieChart } from '../components/Chart'
import { hygieneService } from '../services/api'

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [dailyStats, setDailyStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      const statsRes = await hygieneService.getStats({ days: 30 })
      const dailyRes = await hygieneService.getDailyStats({ days: 30 })
      
      setStats(statsRes.data)
      setDailyStats(dailyRes.data)
      setError(null)
    } catch (err) {
      setError('Failed to fetch data')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="flex justify-center items-center h-64">
      <div className="text-gray-600">Loading...</div>
    </div>
  }

  if (error) {
    return <div className="bg-red-50 p-4 rounded-lg text-red-600">
      {error}
    </div>
  }

  const complianceData = {
    labels: ['Compliant', 'Non-Compliant'],
    datasets: [{
      data: [
        stats?.compliant_events || 0,
        (stats?.total_events || 0) - (stats?.compliant_events || 0)
      ],
      backgroundColor: ['#10b981', '#ef4444'],
      borderColor: ['#059669', '#dc2626'],
      borderWidth: 2,
    }],
  }

  const trendsData = {
    labels: dailyStats?.daily_stats?.map(d => d.date) || [],
    datasets: [{
      label: 'Compliance Rate (%)',
      data: dailyStats?.daily_stats?.map(d => d.compliance_rate) || [],
      borderColor: '#3b82f6',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      borderWidth: 2,
      fill: true,
      tension: 0.4,
    }],
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-800">Dashboard</h2>
          <p className="text-gray-600 mt-2">Overall hand hygiene compliance metrics</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Total Events"
            value={stats?.total_events || 0}
            icon="📊"
            color="blue"
          />
          <StatCard
            title="Compliant (≥20s)"
            value={stats?.compliant_events || 0}
            icon="✅"
            color="green"
          />
          <StatCard
            title="Non-Compliant"
            value={stats?.incomplete_events || 0}
            icon="❌"
            color="red"
          />
          <StatCard
            title="Compliance Rate"
            value={`${(stats?.compliance_rate || 0).toFixed(1)}%`}
            icon="🎯"
            color="yellow"
          />
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <LineChart 
              data={trendsData}
              title="Compliance Trend (Last 30 Days)"
            />
          </div>
          <PieChart
            data={complianceData}
            title="Compliance Distribution"
          />
        </div>

        {/* Additional Stats */}
        <div className="mt-8 bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-bold text-gray-800 mb-4">Additional Metrics</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="border-l-4 border-blue-500 pl-4">
              <p className="text-gray-600 text-sm">Avg Wash Duration</p>
              <p className="text-2xl font-bold text-blue-600">
                {((stats?.total_events || 0) > 0 ? 
                  (stats?.total_events || 0 * (stats?.avg_duration || 0) / (stats?.total_events || 1)) : 0).toFixed(1)}s
              </p>
            </div>
            <div className="border-l-4 border-green-500 pl-4">
              <p className="text-gray-600 text-sm">Success Rate</p>
              <p className="text-2xl font-bold text-green-600">
                {stats?.compliance_rate?.toFixed(1) || 0}%
              </p>
            </div>
            <div className="border-l-4 border-purple-500 pl-4">
              <p className="text-gray-600 text-sm">Last Updated</p>
              <p className="text-lg font-bold text-purple-600">Just now</p>
            </div>
          </div>
        </div>

        {/* Refresh Button */}
        <div className="mt-8 flex justify-center">
          <button
            onClick={fetchData}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition"
          >
            🔄 Refresh Data
          </button>
        </div>
      </div>
    </div>
  )
}
