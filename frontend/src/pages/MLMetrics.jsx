import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { Brain, Activity, TrendingUp, AlertCircle, CheckCircle } from 'lucide-react'

const API_BASE = 'http://localhost:5000/api'

export default function MLMetricsDashboard() {
  const [metrics, setMetrics] = useState(null)
  const [modelStatus, setModelStatus] = useState('unknown')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [refreshInterval, setRefreshInterval] = useState(5) // seconds

  // Fetch model metrics
  useEffect(() => {
    const fetchData = async () => {
      try {
        setError(null)
        
        // Check model status
        const statusRes = await axios.get(`${API_BASE}/ai/model-status`, { timeout: 3000 })
        setModelStatus(statusRes.data.status)
        
        // Get metrics
        if (statusRes.data.model_loaded) {
          const metricsRes = await axios.get(`${API_BASE}/ai/metrics`, { timeout: 3000 })
          setMetrics(metricsRes.data.metrics)
        } else {
          setError('AI model not loaded. Run: python ai/train.py')
        }
      } catch (err) {
        setError(`Failed to fetch metrics: ${err.message}`)
        setModelStatus('error')
      } finally {
        setLoading(false)
      }
    }

    fetchData()

    if (autoRefresh) {
      const interval = setInterval(fetchData, refreshInterval * 1000)
      return () => clearInterval(interval)
    }
  }, [autoRefresh, refreshInterval])

  const resetMetrics = async () => {
    try {
      await axios.post(`${API_BASE}/ai/metrics/reset`)
      setMetrics(null)
      setTimeout(() => window.location.reload(), 1000)
    } catch (err) {
      setError('Failed to reset metrics')
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-purple-800 to-purple-700 p-8 flex items-center justify-center">
        <div className="text-center text-white">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-white mb-4"></div>
          <p>Loading AI Model Metrics...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-purple-800 to-purple-700 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-2">
            <Brain className="w-8 h-8 text-purple-300" />
            <h1 className="text-4xl font-bold text-white">AI Model Dashboard</h1>
          </div>
          <p className="text-purple-200">Real-time Hand Hygiene Detection Metrics</p>
        </div>

        {/* Model Status */}
        <div className="mb-6">
          <div className={`px-6 py-4 rounded-lg flex items-center gap-3 ${
            modelStatus === 'ready' 
              ? 'bg-green-900 text-green-100 border border-green-600' 
              : 'bg-red-900 text-red-100 border border-red-600'
          }`}>
            {modelStatus === 'ready' ? (
              <CheckCircle className="w-6 h-6" />
            ) : (
              <AlertCircle className="w-6 h-6" />
            )}
            <div>
              <p className="font-semibold">
                {modelStatus === 'ready' ? '✅ Model Ready' : '❌ Model Not Loaded'}
              </p>
              {modelStatus !== 'ready' && (
                <p className="text-sm">{error}</p>
              )}
            </div>
          </div>
        </div>

        {error && modelStatus === 'ready' === false && (
          <div className="mb-6 bg-red-900 border border-red-500 text-red-100 px-6 py-4 rounded-lg">
            {error}
          </div>
        )}

        {metrics && (
          <>
            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              {/* Total Predictions */}
              <div className="bg-white rounded-lg shadow-lg p-6">
                <p className="text-gray-600 text-sm">Total Predictions</p>
                <p className="text-3xl font-bold text-gray-800">{metrics.total_predictions}</p>
              </div>

              {/* Hand Washing Detected */}
              <div className="bg-white rounded-lg shadow-lg p-6">
                <p className="text-gray-600 text-sm">Hand Washing Detected</p>
                <p className="text-3xl font-bold text-green-600">{metrics.hand_washing_detected}</p>
                <p className="text-sm text-gray-600 mt-2">
                  {(metrics.hand_washing_detected / metrics.total_predictions * 100 || 0).toFixed(1)}%
                </p>
              </div>

              {/* No Activity */}
              <div className="bg-white rounded-lg shadow-lg p-6">
                <p className="text-gray-600 text-sm">No Activity Detected</p>
                <p className="text-3xl font-bold text-yellow-600">{metrics.no_activity_detected}</p>
                <p className="text-sm text-gray-600 mt-2">
                  {(metrics.no_activity_detected / metrics.total_predictions * 100 || 0).toFixed(1)}%
                </p>
              </div>

              {/* Average Confidence */}
              <div className="bg-white rounded-lg shadow-lg p-6">
                <p className="text-gray-600 text-sm">Average Confidence</p>
                <p className="text-3xl font-bold text-blue-600">
                  {(metrics.average_confidence * 100).toFixed(1)}%
                </p>
              </div>
            </div>

            {/* Detection Rate Chart */}
            <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
              <h2 className="text-xl font-bold text-gray-800 mb-6 flex items-center gap-2">
                <Activity className="w-5 h-5 text-purple-600" />
                Detection Rate
              </h2>

              <div className="flex items-end gap-4 mb-6" style={{ height: '200px' }}>
                {/* Hand Washing Bar */}
                <div className="flex-1">
                  <div className="bg-gradient-to-t from-green-500 to-green-300 rounded-t-lg" 
                       style={{ height: `${Math.max(20, (metrics.hand_washing_detected / metrics.total_predictions * 100 || 0))}%` }}>
                  </div>
                  <p className="text-center text-sm text-gray-700 mt-4 font-semibold">
                    Hand Washing
                  </p>
                  <p className="text-center text-lg font-bold text-green-600">
                    {(metrics.hand_washing_detected / metrics.total_predictions * 100 || 0).toFixed(1)}%
                  </p>
                </div>

                {/* No Activity Bar */}
                <div className="flex-1">
                  <div className="bg-gradient-to-t from-yellow-500 to-yellow-300 rounded-t-lg"
                       style={{ height: `${Math.max(20, (metrics.no_activity_detected / metrics.total_predictions * 100 || 0))}%` }}>
                  </div>
                  <p className="text-center text-sm text-gray-700 mt-4 font-semibold">
                    No Activity
                  </p>
                  <p className="text-center text-lg font-bold text-yellow-600">
                    {(metrics.no_activity_detected / metrics.total_predictions * 100 || 0).toFixed(1)}%
                  </p>
                </div>
              </div>
            </div>

            {/* Recent Predictions */}
            <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
              <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-purple-600" />
                Recent Predictions
              </h2>

              <div className="space-y-3 max-h-60 overflow-y-auto">
                {metrics.recent_predictions && metrics.recent_predictions.length > 0 ? (
                  metrics.recent_predictions.slice().reverse().map((pred, idx) => (
                    <div key={idx} className={`p-3 rounded-lg flex items-center justify-between ${
                      pred.class === 'hand_washing' 
                        ? 'bg-green-50 border border-green-200' 
                        : 'bg-yellow-50 border border-yellow-200'
                    }`}>
                      <div>
                        <p className="font-semibold text-gray-800">
                          {pred.class === 'hand_washing' ? '🧼 Hand Washing' : '⏸️ No Activity'}
                        </p>
                        <p className="text-xs text-gray-600">
                          {new Date(pred.timestamp).toLocaleTimeString()}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-lg font-bold text-gray-800">
                          {(pred.confidence * 100).toFixed(1)}%
                        </p>
                        <div className="w-20 bg-gray-300 rounded-full h-2 mt-1">
                          <div 
                            className={`h-full rounded-full ${
                              pred.class === 'hand_washing' ? 'bg-green-600' : 'bg-yellow-600'
                            }`}
                            style={{ width: `${pred.confidence * 100}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-gray-600 text-center py-4">No predictions yet</p>
                )}
              </div>
            </div>

            {/* Controls */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-lg font-bold text-gray-800 mb-4">Controls</h3>

              <div className="space-y-4">
                {/* Auto-refresh */}
                <div className="flex items-center justify-between">
                  <label className="text-gray-700 font-semibold">Auto-Refresh</label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={autoRefresh}
                      onChange={(e) => setAutoRefresh(e.target.checked)}
                      className="w-4 h-4"
                    />
                    <span className="text-gray-700">{autoRefresh ? 'Enabled' : 'Disabled'}</span>
                  </label>
                </div>

                {/* Refresh interval */}
                {autoRefresh && (
                  <div className="flex items-center justify-between">
                    <label className="text-gray-700 font-semibold">Refresh Interval</label>
                    <select
                      value={refreshInterval}
                      onChange={(e) => setRefreshInterval(parseInt(e.target.value))}
                      className="px-3 py-2 border border-gray-300 rounded-lg"
                    >
                      <option value={1}>1 second</option>
                      <option value={2}>2 seconds</option>
                      <option value={5}>5 seconds</option>
                      <option value={10}>10 seconds</option>
                    </select>
                  </div>
                )}

                {/* Reset button */}
                <button
                  onClick={resetMetrics}
                  className="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded-lg transition"
                >
                  Reset Metrics
                </button>
              </div>
            </div>
          </>
        )}

        {/* Setup Instructions */}
        {modelStatus !== 'ready' && (
          <div className="mt-8 bg-blue-900 border border-blue-600 text-blue-100 p-6 rounded-lg">
            <h3 className="font-bold mb-2">Setup Instructions</h3>
            <ol className="space-y-2 text-sm">
              <li>1. Install AI dependencies: <code className="bg-black px-2 py-1 rounded">pip install -r requirements_ai.txt</code></li>
              <li>2. Train the model: <code className="bg-black px-2 py-1 rounded">python ai/train.py</code></li>
              <li>3. Restart the Flask backend: <code className="bg-black px-2 py-1 rounded">python backend/app.py</code></li>
              <li>4. Refresh this page to see metrics</li>
            </ol>
          </div>
        )}
      </div>
    </div>
  )
}
