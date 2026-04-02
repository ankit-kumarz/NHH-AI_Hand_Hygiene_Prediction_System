import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Lock, Unlock, AlertTriangle, CheckCircle, Clock, User } from 'lucide-react';

const API_BASE = 'http://localhost:5000/api';

const ICUGate = () => {
  const [employees, setEmployees] = useState([]);
  const [selectedEmployee, setSelectedEmployee] = useState('');
  const [accessResult, setAccessResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [gateLocked, setGateLocked] = useState(true);
  const [lockAnimation, setLockAnimation] = useState(false);

  // Load employees on mount
  useEffect(() => {
    fetchEmployees();
  }, []);

  const fetchEmployees = async () => {
    try {
      const response = await axios.get(`${API_BASE}/employees`);
      if (response.data.success) {
        setEmployees(response.data.employees);
      }
    } catch (err) {
      console.error('Failed to fetch employees:', err);
    }
  };

  const handleAccessRequest = async () => {
    if (!selectedEmployee) {
      alert('Please select an employee');
      return;
    }

    try {
      setLoading(true);
      setLockAnimation(true);
      
      // Simulate gate processing
      await new Promise(resolve => setTimeout(resolve, 500));

      const response = await axios.post(`${API_BASE}/access/request`, {
        employee_id: selectedEmployee,
        gate_id: 'icu_main'
      });

      if (response.data.success) {
        const result = response.data.access;
        setAccessResult(result);
        
        // Animate gate based on access result
        if (result.access_granted) {
          setGateLocked(false);
          // Auto-lock after 3 seconds
          setTimeout(() => setGateLocked(true), 3000);
        }
      }
    } catch (err) {
      console.error('Failed to request access:', err);
      setAccessResult({
        access_granted: false,
        message: 'System error. Unable to process access request.'
      });
    } finally {
      setLoading(false);
      setTimeout(() => setLockAnimation(false), 500);
    }
  };

  const getStatusColor = (granted) => {
    return granted 
      ? 'from-green-400 to-green-600' 
      : 'from-red-400 to-red-600';
  };

  const getReasonDescription = (reason) => {
    const reasons = {
      'EMPLOYEE_NOT_FOUND': 'Employee not found in system',
      'NO_RECENT_WASH': 'No hand washing event recorded',
      'WASH_EXPIRED': 'Last wash too long ago (>5 minutes)',
      'WASH_NOT_COMPLIANT': 'Last wash was incomplete (<20 seconds)',
      'LOW_COMPLIANCE_RATE': 'Overall compliance rate too low',
    };
    return reasons[reason] || reason;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 p-6 flex items-center justify-center">
      <div className="max-w-2xl w-full">
        
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Lock className="w-8 h-8 text-red-400" />
            <h1 className="text-4xl font-bold text-white">ICU Access Control</h1>
          </div>
          <p className="text-gray-400">Restricted Area Entry System</p>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* Control Panel */}
          <div className="bg-slate-700 rounded-lg p-6 border border-slate-600">
            <h2 className="text-xl font-bold text-white mb-6">Entry Request</h2>
            
            {/* Employee Selection */}
            <div className="mb-6">
              <label className="block text-gray-300 text-sm font-semibold mb-2">
                <User className="inline w-4 h-4 mr-2" />
                Select Employee
              </label>
              <select
                value={selectedEmployee}
                onChange={(e) => {
                  setSelectedEmployee(e.target.value);
                  setAccessResult(null);
                }}
                className="w-full px-4 py-3 bg-slate-800 text-white border border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">-- Choose an employee --</option>
                {employees.map(emp => (
                  <option key={emp.employee_id} value={emp.employee_id}>
                    {emp.name} - {emp.department} ({emp.role})
                  </option>
                ))}
              </select>
            </div>

            {/* Selected Employee Info */}
            {selectedEmployee && employees.find(e => e.employee_id === selectedEmployee) && (
              <div className="bg-slate-800 rounded p-4 mb-6 border border-slate-600">
                {(() => {
                  const emp = employees.find(e => e.employee_id === selectedEmployee);
                  return (
                    <>
                      <p className="text-white font-bold text-lg">{emp.name}</p>
                      <p className="text-gray-400 text-sm">{emp.department} - {emp.role}</p>
                      <div className="mt-3 flex items-center justify-between">
                        <span className="text-gray-400">Compliance Rate:</span>
                        <span className={`font-bold ${
                          emp.compliance_rate >= 85 ? 'text-green-400' :
                          emp.compliance_rate >= 70 ? 'text-yellow-400' :
                          'text-red-400'
                        }`}>
                          {(emp.compliance_rate || 0).toFixed(1)}%
                        </span>
                      </div>
                    </>
                  );
                })()}
              </div>
            )}

            {/* Request Button */}
            <button
              onClick={handleAccessRequest}
              disabled={!selectedEmployee || loading}
              className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-bold py-3 px-4 rounded-lg disabled:from-gray-500 disabled:to-gray-600 disabled:cursor-not-allowed transition-all"
            >
              {loading ? 'Processing...' : 'Request Entry'}
            </button>
          </div>

          {/* Gate Status Display */}
          <div className="flex flex-col items-center justify-center">
            {/* Gate Visual */}
            <div className="relative mb-8">
              {/* Gate Door */}
              <div className={`relative w-32 h-48 border-4 border-gray-600 rounded-lg overflow-hidden ${lockAnimation ? 'animate-bounce' : ''}`}>
                <div className={`absolute inset-0 transition-all duration-500 ${
                  gateLocked 
                    ? 'bg-red-900' 
                    : 'bg-green-900'
                }`}>
                  {gateLocked ? (
                    <Lock className="w-full h-full text-red-300 p-4" />
                  ) : (
                    <Unlock className="w-full h-full text-green-300 p-4" />
                  )}
                </div>

                {/* Status Light */}
                <div className={`absolute top-4 right-4 w-4 h-4 rounded-full ${
                  gateLocked 
                    ? 'bg-red-500 animate-pulse' 
                    : 'bg-green-500 animate-pulse'
                }`} />
              </div>

              {/* Lock Status Text */}
              <p className="text-center text-white font-bold mt-4">
                {gateLocked ? 'LOCKED' : 'UNLOCKED'}
              </p>
            </div>

            {/* Access Result Message */}
            {accessResult && (
              <div className={`w-full rounded-lg p-6 border-2 transition-all ${
                accessResult.access_granted
                  ? 'bg-green-900 border-green-500'
                  : 'bg-red-900 border-red-500'
              }`}>
                {/* Status Indicator */}
                <div className="flex items-center justify-center mb-4">
                  {accessResult.access_granted ? (
                    <div className="flex items-center gap-2">
                      <CheckCircle className="w-8 h-8 text-green-400" />
                      <span className="text-xl font-bold text-green-400">ACCESS GRANTED</span>
                    </div>
                  ) : (
                    <div className="flex items-center gap-2">
                      <AlertTriangle className="w-8 h-8 text-red-400" />
                      <span className="text-xl font-bold text-red-400">ACCESS DENIED</span>
                    </div>
                  )}
                </div>

                {/* Message */}
                <p className={`text-center text-lg font-semibold ${
                  accessResult.access_granted ? 'text-green-200' : 'text-red-200'
                } mb-4`}>
                  {accessResult.message}
                </p>

                {/* Details */}
                <div className={`text-sm ${accessResult.access_granted ? 'text-green-300' : 'text-red-300'}`}>
                  {accessResult.last_wash_time && (
                    <div className="flex items-center justify-between mb-2">
                      <span>Last Wash:</span>
                      <span>{new Date(accessResult.last_wash_time).toLocaleTimeString()}</span>
                    </div>
                  )}
                  {accessResult.last_wash_duration !== null && (
                    <div className="flex items-center justify-between mb-2">
                      <span>Duration:</span>
                      <span>{accessResult.last_wash_duration?.toFixed(1) || 0}s</span>
                    </div>
                  )}
                  {accessResult.denial_reason && (
                    <div className="flex items-center justify-between border-t border-opacity-30 pt-2">
                      <span>Reason:</span>
                      <span className="text-right">{getReasonDescription(accessResult.denial_reason)}</span>
                    </div>
                  )}
                </div>

                {/* Action Buttons */}
                {!accessResult.access_granted && (
                  <div className="mt-4 flex gap-2">
                    <button
                      onClick={() => setAccessResult(null)}
                      className="flex-1 bg-red-700 hover:bg-red-800 text-white py-2 px-3 rounded text-sm font-semibold transition"
                    >
                      Dismiss
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Compliance Guidelines */}
        <div className="mt-12 bg-slate-700 rounded-lg p-6 border border-slate-600">
          <h3 className="text-white font-bold mb-4 flex items-center gap-2">
            <Clock className="w-5 h-5" />
            ICU Access Requirements
          </h3>
          <ul className="space-y-2 text-gray-300 text-sm">
            <li>✓ Hand wash within last 5 minutes</li>
            <li>✓ Complete wash (20+ seconds required)</li>
            <li>✓ Overall compliance rate ≥70%</li>
            <li>✗ Multiple access denials will trigger supervisor notification</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default ICUGate;
