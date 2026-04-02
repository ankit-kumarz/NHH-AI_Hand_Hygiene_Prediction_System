"""
Real-time Events System using Flask-SocketIO
Handles WebSocket connections and broadcasts alerts
"""

from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime
import json

# Global SocketIO instance
socketio = None

def init_socketio(app):
    """Initialize SocketIO with Flask app"""
    global socketio
    socketio = SocketIO(
        app,
        cors_allowed_origins="*",
        async_mode='threading',
        ping_timeout=60,
        ping_interval=25
    )
    
    register_handlers()
    return socketio


def register_handlers():
    """Register WebSocket event handlers"""
    
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection"""
        print(f'🟢 Client connected')
        emit('connection_response', {
            'status': 'connected',
            'timestamp': datetime.utcnow().isoformat(),
            'message': 'Connected to real-time server'
        })
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        print(f'🔴 Client disconnected')
    
    @socketio.on('join_room')
    def on_join_room(data):
        """Join a specific room (e.g., department)"""
        room = data.get('room', 'general')
        join_room(room)
        print(f'👤 User joined room: {room}')
        emit('room_joined', {
            'room': room,
            'timestamp': datetime.utcnow().isoformat()
        }, room=room)
    
    @socketio.on('leave_room')
    def on_leave_room(data):
        """Leave a specific room"""
        room = data.get('room', 'general')
        leave_room(room)
        print(f'👤 User left room: {room}')
    
    @socketio.on('test_event')
    def handle_test(data):
        """Handle test events"""
        emit('test_response', {
            'received': data,
            'timestamp': datetime.utcnow().isoformat()
        })


def broadcast_detection_event(event_data):
    """
    Broadcast detection event to all connected clients
    
    Args:
        event_data: Dictionary with event information
    """
    if socketio is None:
        return
    
    socketio.emit('detection_event', {
        'timestamp': datetime.utcnow().isoformat(),
        'data': event_data
    }, broadcast=True)


def broadcast_completion_alert(alert_data):
    """
    Broadcast handwash completion alert
    
    Args:
        alert_data: Dictionary with alert information
    """
    if socketio is None:
        return
    
    socketio.emit('completion_alert', {
        'type': 'success',
        'timestamp': datetime.utcnow().isoformat(),
        'data': alert_data
    }, broadcast=True)


def broadcast_failure_alert(alert_data):
    """
    Broadcast handwash failure alert
    
    Args:
        alert_data: Dictionary with alert information
    """
    if socketio is None:
        return
    
    socketio.emit('failure_alert', {
        'type': 'warning',
        'timestamp': datetime.utcnow().isoformat(),
        'data': alert_data
    }, broadcast=True)


def broadcast_status_update(status_data):
    """
    Broadcast real-time status update
    
    Args:
        status_data: Dictionary with status information
    """
    if socketio is None:
        return
    
    socketio.emit('status_update', {
        'timestamp': datetime.utcnow().isoformat(),
        'data': status_data
    }, broadcast=True)


def broadcast_system_alert(message, alert_type='info'):
    """
    Broadcast system-wide alert
    
    Args:
        message: Alert message
        alert_type: Type of alert (info, warning, error, success)
    """
    if socketio is None:
        return
    
    socketio.emit('system_alert', {
        'type': alert_type,
        'message': message,
        'timestamp': datetime.utcnow().isoformat()
    }, broadcast=True)


if __name__ == "__main__":
    print("Real-time module loaded")
