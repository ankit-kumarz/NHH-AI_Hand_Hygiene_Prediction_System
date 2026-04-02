import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Search, Filter, Users, TrendingUp, Clock, AlertCircle } from 'lucide-react';
import EmployeeCard from '../components/EmployeeCard';

const API_BASE = 'http://localhost:5000/api';

const EmployeeTracker = () => {
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDepartment, setSelectedDepartment] = useState('all');
  const [departments, setDepartments] = useState([]);
  const [selectedEmployee, setSelectedEmployee] = useState(null);
  const [employeeHistory, setEmployeeHistory] = useState([]);

  // Load employees on mount
  useEffect(() => {
    fetchEmployees();
  }, []);

  const fetchEmployees = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE}/employees`);
      if (response.data.success) {
        setEmployees(response.data.employees);
        
        // Extract unique departments
        const depts = [...new Set(response.data.employees.map(e => e.department))];
        setDepartments(depts);
      }
    } catch (err) {
      setError('Failed to fetch employees');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchEmployeeDetails = async (employeeId) => {
    try {
      const response = await axios.get(`${API_BASE}/employees/${employeeId}/history?limit=10`);
      if (response.data.success) {
        setEmployeeHistory(response.data.events);
        setSelectedEmployee(employeeId);
      }
    } catch (err) {
      console.error('Failed to fetch employee history:', err);
    }
  };

  const sendReminder = async (employeeId) => {
    try {
      await axios.post(`${API_BASE}/alerts`, {
        employee_id: employeeId,
        alert_type: 'REMINDER',
        message: 'This is a reminder to wash your hands before entering restricted areas.'
      });
      alert('Reminder sent successfully');
    } catch (err) {
      console.error('Failed to send reminder:', err);
    }
  };

  // Filter employees
  let filteredEmployees = employees;
  
  if (selectedDepartment !== 'all') {
    filteredEmployees = filteredEmployees.filter(e => e.department === selectedDepartment);
  }
  
  if (searchTerm) {
    filteredEmployees = filteredEmployees.filter(e =>
      e.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      e.employee_id.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }

  // Sort by compliance rate (lowest first - needs attention)
  filteredEmployees = filteredEmployees.sort((a, b) => 
    (a.compliance_rate || 0) - (b.compliance_rate || 0)
  );

  const getComplianceColor = (rate) => {
    if (rate >= 85) return 'text-green-600 bg-green-50';
    if (rate >= 70) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  const getComplianceBadgeColor = (rate) => {
    if (rate >= 85) return 'bg-green-100 text-green-800';
    if (rate >= 70) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Loading employees...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <Users className="w-8 h-8 text-blue-600" />
            <h1 className="text-3xl font-bold text-gray-800">Employee Tracker</h1>
          </div>
          <p className="text-gray-600">Monitor hand hygiene compliance across all staff members</p>
        </div>

        {/* Stats Summary */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Total Employees</p>
                <p className="text-2xl font-bold text-gray-800">{employees.length}</p>
              </div>
              <Users className="w-8 h-8 text-blue-400" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">High Compliance (≥85%)</p>
                <p className="text-2xl font-bold text-green-600">
                  {employees.filter(e => (e.compliance_rate || 0) >= 85).length}
                </p>
              </div>
              <TrendingUp className="w-8 h-8 text-green-400" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Needs Attention (&lt;70%)</p>
                <p className="text-2xl font-bold text-red-600">
                  {employees.filter(e => (e.compliance_rate || 0) < 70).length}
                </p>
              </div>
              <AlertCircle className="w-8 h-8 text-red-400" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Avg. Compliance</p>
                <p className="text-2xl font-bold text-blue-600">
                  {(employees.reduce((sum, e) => sum + (e.compliance_rate || 0), 0) / employees.length).toFixed(1)}%
                </p>
              </div>
              <Clock className="w-8 h-8 text-blue-400" />
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search by name or employee ID..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Filter className="w-5 h-5 text-gray-600" />
              <select
                value={selectedDepartment}
                onChange={(e) => setSelectedDepartment(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Departments</option>
                {departments.map(dept => (
                  <option key={dept} value={dept}>{dept}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Employees Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredEmployees.map(employee => (
            <div
              key={employee.id}
              onClick={() => fetchEmployeeDetails(employee.employee_id)}
              className="cursor-pointer transform hover:scale-105 transition-transform"
            >
              <EmployeeCard employee={employee} onSendReminder={sendReminder} />
            </div>
          ))}
        </div>

        {filteredEmployees.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">No employees found matching your criteria</p>
          </div>
        )}

        {/* Selected Employee Details Modal */}
        {selectedEmployee && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg max-w-2xl w-full max-h-96 overflow-y-auto">
              <div className="sticky top-0 bg-white border-b p-4 flex justify-between items-center">
                <h2 className="text-xl font-bold">Employee Details</h2>
                <button
                  onClick={() => setSelectedEmployee(null)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ✕
                </button>
              </div>

              <div className="p-6">
                {/* Employee header */}
                <div className="mb-6 pb-4 border-b">
                  {employees.find(e => e.employee_id === selectedEmployee) && (
                    <>
                      <h3 className="text-2xl font-bold mb-2">
                        {employees.find(e => e.employee_id === selectedEmployee)?.name}
                      </h3>
                      <div className="flex gap-4 mb-4">
                        <span className="inline-block px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                          {employees.find(e => e.employee_id === selectedEmployee)?.role}
                        </span>
                        <span className="inline-block px-3 py-1 bg-gray-100 text-gray-800 rounded-full text-sm">
                          {employees.find(e => e.employee_id === selectedEmployee)?.department}
                        </span>
                        <span className={`inline-block px-3 py-1 rounded-full text-sm font-bold ${getComplianceBadgeColor(employees.find(e => e.employee_id === selectedEmployee)?.compliance_rate || 0)}`}>
                          {(employees.find(e => e.employee_id === selectedEmployee)?.compliance_rate || 0).toFixed(1)}%
                        </span>
                      </div>
                    </>
                  )}
                </div>

                {/* Wash History */}
                <div>
                  <h4 className="font-bold text-lg mb-4">Recent Wash Events</h4>
                  {employeeHistory.length > 0 ? (
                    <div className="space-y-3">
                      {employeeHistory.map((event, idx) => (
                        <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <div>
                            <p className="text-sm text-gray-600">
                              {new Date(event.timestamp).toLocaleString()}
                            </p>
                            <p className="font-semibold">Duration: {event.duration?.toFixed(1) || 0}s</p>
                          </div>
                          <span className={`px-3 py-1 rounded-full text-sm font-bold ${event.compliant ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                            {event.compliant ? 'Compliant' : 'Incomplete'}
                          </span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500">No wash events found</p>
                  )}
                </div>

                <button
                  onClick={() => setSelectedEmployee(null)}
                  className="mt-6 w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default EmployeeTracker;
