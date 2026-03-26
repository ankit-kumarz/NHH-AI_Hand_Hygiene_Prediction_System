import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
})

export const hygieneService = {
  // Logging
  logEvent: (data) => api.post('/log', data),
  
  // Fetching events
  getEvents: (params) => api.get('/logs', { params }),
  getEventById: (id) => api.get(`/logs/${id}`),
  
  // Statistics
  getStats: (params) => api.get('/stats', { params }),
  getDailyStats: (params) => api.get('/stats/daily', { params }),
  getUserStats: (userId, params) => api.get(`/stats/user/${userId}`, { params }),
  
  // Users
  createUser: (data) => api.post('/users', data),
  getUser: (userId) => api.get(`/users/${userId}`),
  
  // Health
  healthCheck: () => api.get('/health'),
}

export default api
