"""
Phase 4 Integration - Connect AI Detection with Real-time Alerts
Sends detection results from Phase 1 to Phase 4 WebSocket system
"""

import requests
from realtime.events import (
    broadcast_completion_alert,
    broadcast_failure_alert,
    broadcast_status_update
)


class RealtimeEventEmitter:
    """
    Emits real-time events from AI detection to connected clients
    """
    
    def __init__(self, api_url='http://localhost:5000'):
        self.api_url = api_url
    
    def on_hand_detected(self, duration, progress):
        """
        Emit when hands are detected
        
        Args:
            duration: Time since detection started
            progress: Progress percentage (0-100)
        """
        broadcast_status_update({
            'event': 'hand_detected',
            'duration': round(duration, 1),
            'progress': round(progress, 1),
            'status': 'Detecting'
        })
    
    def on_washing_started(self):
        """Emit when washing motion detected"""
        broadcast_status_update({
            'event': 'washing_started',
            'status': 'Washing'
        })
    
    def on_washing_progress(self, elapsed, required=20):
        """
        Emit washing progress
        
        Args:
            elapsed: Elapsed time in seconds
            required: Required time (default 20s)
        """
        progress = min((elapsed / required) * 100, 100)
        broadcast_status_update({
            'event': 'washing_progress',
            'elapsed': round(elapsed, 1),
            'required': required,
            'progress': round(progress, 1)
        })
    
    def on_completion(self, duration, user_id='system', location=None):
        """
        Emit when handwashing completed successfully
        
        Args:
            duration: Total wash duration
            user_id: User identifier
            location: Physical location
        """
        broadcast_completion_alert({
            'duration': round(duration, 1),
            'user_id': user_id,
            'location': location,
            'message': f'✅ Excellent! Proper handwashing completed ({duration:.1f}s)'
        })
        
        # Log to backend
        try:
            requests.post(
                f'{self.api_url}/api/log',
                json={
                    'user_id': user_id,
                    'duration': duration,
                    'status': 'completed',
                    'location': location
                },
                timeout=5
            )
        except Exception as e:
            print(f'❌ Failed to log completion: {e}')
    
    def on_failure(self, duration, user_id='system', location=None):
        """
        Emit when handwashing fails (< 20 seconds)
        
        Args:
            duration: Actual wash duration
            user_id: User identifier
            location: Physical location
        """
        broadcast_failure_alert({
            'duration': round(duration, 1),
            'user_id': user_id,
            'location': location,
            'message': f'⚠️ Insufficient wash time ({duration:.1f}s < 20s). Retry!'
        })
        
        # Log to backend
        try:
            requests.post(
                f'{self.api_url}/api/log',
                json={
                    'user_id': user_id,
                    'duration': duration,
                    'status': 'incomplete',
                    'location': location
                },
                timeout=5
            )
        except Exception as e:
            print(f'❌ Failed to log failure: {e}')
    
    def on_hands_lost(self):
        """Emit when hands disappear from frame"""
        broadcast_status_update({
            'event': 'hands_lost',
            'status': 'Idle'
        })


if __name__ == "__main__":
    print("Phase 4 Integration module loaded")
