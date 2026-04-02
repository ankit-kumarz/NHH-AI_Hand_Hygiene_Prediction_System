import React from 'react';
import { TrendingUp, AlertCircle, Zap } from 'lucide-react';

const EmployeeCard = ({ employee, onSendReminder }) => {
  const complianceRate = employee.compliance_rate || 0;
  
  const getStatusColor = () => {
    if (complianceRate >= 85) return 'border-green-500 bg-green-50';
    if (complianceRate >= 70) return 'border-yellow-500 bg-yellow-50';
    return 'border-red-500 bg-red-50';
  };

  const getComplianceColor = () => {
    if (complianceRate >= 85) return 'text-green-600';
    if (complianceRate >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getProgressColor = () => {
    if (complianceRate >= 85) return 'bg-green-500';
    if (complianceRate >= 70) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getStatusBadge = () => {
    if (complianceRate >= 85) return { text: 'Excellent', bg: 'bg-green-100', text_color: 'text-green-800' };
    if (complianceRate >= 70) return { text: 'Good', bg: 'bg-yellow-100', text_color: 'text-yellow-800' };
    return { text: 'Needs Attention', bg: 'bg-red-100', text_color: 'text-red-800' };
  };

  const status = getStatusBadge();

  return (
    <div className={`rounded-lg border-2 shadow-lg overflow-hidden transition-all hover:shadow-xl ${getStatusColor()}`}>
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-4">
        <h3 className="font-bold text-lg">{employee.name}</h3>
        <p className="text-blue-100 text-sm">{employee.employee_id}</p>
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Department & Role */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-gray-600 uppercase">Department</span>
            <span className="inline-block px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-semibold">
              {employee.department}
            </span>
          </div>
          <p className="text-sm text-gray-600">{employee.role}</p>
        </div>

        {/* Compliance Rate */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-gray-600 uppercase">Compliance Rate</span>
            <span className={`text-2xl font-bold ${getComplianceColor()}`}>
              {complianceRate.toFixed(1)}%
            </span>
          </div>

          {/* Progress Bar */}
          <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
            <div
              className={`h-full transition-all ${getProgressColor()}`}
              style={{ width: `${Math.min(complianceRate, 100)}%` }}
            />
          </div>
        </div>

        {/* Status Badge */}
        <div className="mb-4">
          <span className={`inline-block px-3 py-1 rounded-full text-xs font-bold ${status.bg} ${status.text_color}`}>
            {status.text}
          </span>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 gap-3 mb-4 text-sm">
          <div className="bg-gray-100 rounded p-2">
            <p className="text-gray-600 text-xs">Total Washes</p>
            <p className="font-bold text-gray-800">{employee.total_washes || 0}</p>
          </div>
          <div className="bg-gray-100 rounded p-2">
            <p className="text-gray-600 text-xs">Alerts</p>
            <p className="font-bold text-gray-800">{employee.alert_count || 0}</p>
          </div>
        </div>

        {/* Last Wash */}
        {employee.last_wash_time && (
          <div className="mb-4 p-2 bg-gray-100 rounded text-sm">
            <p className="text-gray-600 text-xs mb-1">Last Wash</p>
            <p className="font-semibold text-gray-800">
              {new Date(employee.last_wash_time).toLocaleTimeString()}
            </p>
            <p className={`text-xs font-bold mt-1 ${employee.last_wash_compliant ? 'text-green-600' : 'text-red-600'}`}>
              {employee.last_wash_compliant ? '✓ Compliant' : '✗ Incomplete'}
            </p>
          </div>
        )}

        {/* Actions */}
        <button
          onClick={() => onSendReminder(employee.employee_id)}
          className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white py-2 px-3 rounded-lg transition font-semibold text-sm"
        >
          <Zap className="w-4 h-4" />
          Send Reminder
        </button>

        {/* Warning Indicator */}
        {complianceRate < 70 && (
          <div className="mt-3 flex items-center gap-2 p-2 bg-red-100 rounded border border-red-300 text-red-800 text-xs">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>Requires supervisor attention</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default EmployeeCard;
