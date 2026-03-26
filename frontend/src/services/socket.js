import io from 'socket.io-client'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

// Initialize Socket.IO connection
const socket = io(API_BASE_URL, {
  reconnection: true,
  reconnectionDelay: 1000,
  reconnectionDelayMax: 5000,
  reconnectionAttempts: 5,
  transports: ['websocket', 'polling']
})

// Socket event listeners
export const socketEvents = {
  // Connection events
  onConnect: (callback) => socket.on('connect', callback),
  onDisconnect: (callback) => socket.on('disconnect', callback),
  onConnectionResponse: (callback) => socket.on('connection_response', callback),
  
  // Real-time alerts
  onCompletionAlert: (callback) => socket.on('completion_alert', callback),
  onFailureAlert: (callback) => socket.on('failure_alert', callback),
  onDetectionEvent: (callback) => socket.on('detection_event', callback),
  
  // Status updates
  onStatusUpdate: (callback) => socket.on('status_update', callback),
  onSystemAlert: (callback) => socket.on('system_alert', callback),
  
  // Room events
  onRoomJoined: (callback) => socket.on('room_joined', callback),
}

// Socket event emitters
export const socketEmit = {
  joinRoom: (room) => socket.emit('join_room', { room }),
  leaveRoom: (room) => socket.emit('leave_room', { room }),
  testEvent: (data) => socket.emit('test_event', data),
}

// Socket connection utilities
export const socketUtils = {
  isConnected: () => socket.connected,
  getSocketId: () => socket.id,
  disconnect: () => socket.disconnect(),
  connect: () => socket.connect(),
}

export default socket
