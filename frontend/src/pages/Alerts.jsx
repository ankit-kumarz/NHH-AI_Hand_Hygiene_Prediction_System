import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { AlertTriangle, CheckCircle, Clock, User, Filter, RefreshCw } from 'lucide-react';

const API_BASE = 'http://localhost:5000/api';

const Alerts = () => {
  const [alerts, setAlerts] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterType, setFilterType] = useState('all');
  const [lastUpdated, setLastUpdated] = useState(new Date());

  // Load alerts on mount and set up auto-refresh
  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchAlerts = async () => {
    try {
      const response = await axios.get(`${API_BASE}/alerts/unacknowledged`);
      if (response.data.success) {
        setAlerts(response.data.alerts);
        setSummary(response.data.summary);
        setLastUpdated(new Date());
      }
    } catch (err) {
      setError('Failed to fetch alerts');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const acknowledgeAlert = async (alertId) => {
    try {
      await axios.put(`${API_BASE}/alerts/${alertId}/acknowledge`, {
        acknowledged_by: 'current_user'
      });
      
      // Remove acknowledged alert from display
      setAlerts(alerts.filter(a => a.id !== alertId));
      
      // Refresh to get updated summary
      await fetchAlerts();
    } catch (err) {
      console.error('Failed to acknowledge alert:', err);
    }
  };

  const getAlertIcon = (alertType) => {
    switch (alertType) {
      case 'REMINDER':
        return <Clock className="w-5 h-5 text-blue-600" />;
      case 'TRAINING_REQUIRED':
        return <AlertTriangle className="w-5 h-5 text-yellow-600" />;
      case 'SUPERVISOR_NOTIFICATION':
        return <AlertTriangle className="w-5 h-5 text-red-600" />;
      case 'ACCESS_VIOLATION':
        return <AlertTriangle className="w-5 h-5 text-red-700" />;
      default:
        return <AlertTriangle className="w-5 h-5 text-gray-600" />;
    }
  };

  const getAlertColor = (alertType) => {
    switch (alertType) {
      case 'REMINDER':
        return 'bg-blue-50 border-blue-200';
      case 'TRAINING_REQUIRED':
        return 'bg-yellow-50 border-yellow-200';
      case 'SUPERVISOR_NOTIFICATION':
        return 'bg-red-50 border-red-200';
      case 'ACCESS_VIOLATION':
        return 'bg-red-100 border-red-300';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  const getAlertBadgeColor = (alertType) => {
    switch (alertType) {
      case 'REMINDER':
        return 'bg-blue-100 text-blue-800';
      case 'TRAINING_REQUIRED':
        return 'bg-yellow-100 text-yellow-800';
      case 'SUPERVISOR_NOTIFICATION':
        return 'bg-red-100 text-red-800';
      case 'ACCESS_VIOLATION':
        return 'bg-red-200 text-red-900';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // Filter alerts
  let filteredAlerts = alerts;
  if (filterType !== 'all') {
    filteredAlerts = alerts.filter(a => a.alert_type === filterType);
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-red-600"></div>
          <p className="mt-4 text-gray-600">Loading alerts...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 to-orange-100 p-6">
      <div className="max-w-5xl mx-auto">
        
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <AlertTriangle className="w-8 h-8 text-red-600" />
            <h1 className="text-3xl font-bold text-gray-800">Alerts & Notifications</h1>
          </div>
          <p className="text-gray-600">Monitor compliance violations and training requirements</p>
          <p className="text-gray-500 text-sm mt-2">Last updated: {lastUpdated.toLocaleTimeString()}</p>
        </div>

        {/* Summary Cards */}
        {summary && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-white rounded-lg shadow p-4 border-l-4 border-red-600">
              <p className="text-gray-600 text-sm">Total Unacknowledged</p>
              <p className="text-3xl font-bold text-red-600">{summary.total_unacknowledged}</p>
            </div>

            {summary.by_type['REMINDER'] && (
              <div className="bg-white rounded-lg shadow p-4 border-l-4 border-blue-600">
                <p className="text-gray-600 text-sm">Reminders</p>
                <p className="text-3xl font-bold text-blue-600">{summary.by_type['REMINDER']}</p>
              </div>
            )}

            {summary.by_type['TRAINING_REQUIRED'] && (
              <div className="bg-white rounded-lg shadow p-4 border-l-4 border-yellow-600">
                <p className="text-gray-600 text-sm">Training Required</p>
                <p className="text-3xl font-bold text-yellow-600">{summary.by_type['TRAINING_REQUIRED']}</p>
              </div>
            )}

            {summary.by_type['SUPERVISOR_NOTIFICATION'] && (
              <div className="bg-white rounded-lg shadow p-4 border-l-4 border-red-700">
                <p className="text-gray-600 text-sm">Supervisor Alerts</p>
                <p className="text-3xl font-bold text-red-700">{summary.by_type['SUPERVISOR_NOTIFICATION']}</p>
              </div>
            )}
          </div>
        )}

        {/* Controls */}
        <div className="bg-white rounded-lg shadow p-4 mb-6 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-gray-600" />
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
            >
              <option value="all">All Alerts</option>
              <option value="REMINDER">Reminders</option>
              <option value="TRAINING_REQUIRED">Training Required</option>
              <option value="SUPERVISOR_NOTIFICATION">Supervisor Notifications</option>
              <option value="ACCESS_VIOLATION">Access Violations</option>
            </select>
          </div>

          <button
            onClick={fetchAlerts}
            className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Alerts List */}
        <div className="space-y-4">
          {filteredAlerts.length > 0 ? (
            filteredAlerts.map(alert => (
              <div
                key={alert.id}
                className={`rounded-lg border-2 p-4 transition-all hover:shadow-lg ${getAlertColor(alert.alert_type)}`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4 flex-1">
                    <div className="mt-1">
                      {getAlertIcon(alert.alert_type)}
                    </div>

                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className={`inline-block px-2 py-1 rounded text-xs font-semibold ${getAlertBadgeColor(alert.alert_type)}`}>
                          {alert.alert_type.replace(/_/g, ' ')}
                        </span>
                        <span className="text-gray-500 text-sm">
                          {new Date(alert.created_at).toLocaleString()}
                        </span>
                      </div>

                      <p className="text-gray-800 font-semibold mb-2">{alert.message}</p>

                      <div className="flex items-center gap-4 text-sm text-gray-600">
                        {alert.name && (
                          <div className="flex items-center gap-1">
                            <User className="w-4 h-4" />
                            <span>{alert.name}</span>
                          </div>
                        )}
                        {alert.department && (
                          <div>
                            <span className="text-gray-500">Department:</span>
                            <span className="ml-1 font-semibold">{alert.department}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  <button
                    onClick={() => acknowledgeAlert(alert.id)}
                    className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-3 py-2 rounded-lg transition whitespace-nowrap ml-4"
                  >
                    <CheckCircle className="w-4 h-4" />
                    <span className="text-sm font-semibold">Acknowledge</span>
                  </button>
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-12 bg-white rounded-lg">
              <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
              <p className="text-gray-500 text-lg font-semibold">All Caught Up!</p>
              <p className="text-gray-400">No unacknowledged alerts at this time</p>
            </div>
          )}
        </div>

        {/* Top Alerted Employees */}
        {summary?.top_alerted_employees && summary.top_alerted_employees.length > 0 && (
          <div className="mt-8 bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-800 mb-4">Employees Requiring Attention</h2>
            <div className="space-y-3">
              {summary.top_alerted_employees.map((emp, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 bg-red-50 rounded-lg border border-red-200">
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 rounded-full bg-red-600"></div>
                    <span className="font-semibold text-gray-800">{emp.name}</span>
                  </div>
                  <span className="bg-red-600 text-white px-3 py-1 rounded-full text-sm font-bold">
                    {emp.alert_count} alerts
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Alerts;
