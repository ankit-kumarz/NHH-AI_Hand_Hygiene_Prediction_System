import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
})

export const hygieneService = {
  // Health
  healthCheck: () => api.get('/health'),
  
  // Employees
  getEmployees: () => api.get('/employees'),
  getEmployee: (employeeId) => api.get(`/employees/${employeeId}`),
  createEmployee: (data) => api.post('/employees', data),
  updateEmployee: (employeeId, data) => api.put(`/employees/${employeeId}`, data),
  getEmployeeHistory: (employeeId, params) => api.get(`/employees/${employeeId}/history`, { params }),
  getEmployeesByDepartment: (department) => api.get(`/employees/department/${department}`),
  
  // Wash Events
  logWashEvent: (data) => api.post('/wash-event', data),
  getWashEvents: (employeeId, params) => api.get(`/wash-events/${employeeId}`, { params }),
  
  // Statistics
  getStats: (params) => api.get('/stats/overall', { params }),
  getDailyStats: (params) => api.get('/stats/daily', { params }),
  getDepartmentStats: (department, params) => api.get(`/stats/department/${department}`, { params }),
  
  // Alerts
  getAlerts: (params) => api.get('/alerts', { params }),
  getUnacknowledgedAlerts: () => api.get('/alerts/unacknowledged'),
  createAlert: (data) => api.post('/alerts', data),
  acknowledgeAlert: (alertId) => api.put(`/alerts/${alertId}/acknowledge`),
  
  // Access Control
  requestAccess: (data) => api.post('/access/request', data),
  getAccessLogs: (params) => api.get('/access/logs', { params }),
}

export default api

