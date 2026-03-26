"""
Test WebSocket connections and real-time events
"""

import socketio
import json
import time

# Connect as client
sio = socketio.Client(reconnection=True)

@sio.event
def connect():
    print('🟢 Connected to server')
    print('Waiting for real-time events...\n')

@sio.event
def connection_response(data):
    print(f'📨 Connection Response: {json.dumps(data, indent=2)}')

@sio.event
def completion_alert(data):
    print(f'✅ Completion Alert: {json.dumps(data, indent=2)}')

@sio.event
def failure_alert(data):
    print(f'⚠️ Failure Alert: {json.dumps(data, indent=2)}')

@sio.event
def detection_event(data):
    print(f'👋 Detection Event: {json.dumps(data, indent=2)}')

@sio.event
def status_update(data):
    print(f'📊 Status Update: {json.dumps(data, indent=2)}')

@sio.event
def system_alert(data):
    print(f'🔔 System Alert: {json.dumps(data, indent=2)}')

@sio.event
def disconnect():
    print('\n🔴 Disconnected from server')

if __name__ == '__main__':
    try:
        print('🏥 Connecting to Hand Hygiene WebSocket Server...')
        print('Server: ws://localhost:5000\n')
        
        sio.connect('http://localhost:5000')
        
        print('=' * 70)
        print('Real-time Event Monitor Active')
        print('=' * 70)
        print('Listening for events (Press Ctrl+C to exit)...\n')
        
        # Keep connection open
        sio.wait()
        
    except Exception as e:
        print(f'❌ Connection Error: {e}')
        print('Make sure Flask server is running on port 5000')
