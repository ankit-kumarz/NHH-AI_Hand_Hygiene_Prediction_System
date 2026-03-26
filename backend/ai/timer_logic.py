"""
Timer Logic for Hand Hygiene Detection
Tracks hand detection duration and compliance with WHO 20-second rule
"""

import time
from enum import Enum
from typing import Dict


class HygieneStatus(Enum):
    """Status of hand hygiene event"""
    IDLE = "Idle"  # No hands detected
    DETECTED = "Detected"  # Hands detected, timer started
    WASHING = "Washing"  # Timer running
    COMPLETED = "Completed ✓"  # 20+ seconds achieved
    FAILED = "Failed ✗"  # Less than 20 seconds


class HygieneTimer:
    """
    Manages hand hygiene event timing
    Tracks duration and compliance with WHO 20-second rule
    """
    
    # WHO Standard: 20 seconds for effective handwashing
    REQUIRED_DURATION = 20  # seconds
    
    def __init__(self):
        """Initialize timer"""
        self.start_time = None
        self.elapsed_time = 0
        self.status = HygieneStatus.IDLE
        self.event_log = []
        self.current_event = {}
        
    def start_detection(self):
        """Start timer when hands are detected"""
        if self.status == HygieneStatus.IDLE:
            self.start_time = time.time()
            self.elapsed_time = 0
            self.status = HygieneStatus.DETECTED
            self.current_event = {
                'start_time': self.start_time,
                'duration': 0,
                'status': 'in_progress'
            }
            return True
        return False
    
    def update_timer(self, hands_detected: bool) -> Dict:
        """
        Update timer based on hand detection status
        
        Args:
            hands_detected: Whether hands are currently detected
            
        Returns:
            Dictionary with current status and elapsed time
        """
        
        # Hands detected
        if hands_detected:
            if self.status == HygieneStatus.IDLE:
                self.start_detection()
            
            # Calculate elapsed time
            self.elapsed_time = time.time() - self.start_time
            
            # Check if 20 seconds achieved
            if self.elapsed_time >= self.REQUIRED_DURATION:
                self.status = HygieneStatus.COMPLETED
            else:
                self.status = HygieneStatus.WASHING
        
        # No hands detected
        else:
            if self.status != HygieneStatus.IDLE:
                # Event ended
                if self.elapsed_time < self.REQUIRED_DURATION:
                    self.status = HygieneStatus.FAILED
                
                # Log event
                self.log_event()
                
                # Reset
                self.reset()
        
        return {
            'status': self.status.value,
            'elapsed_time': round(self.elapsed_time, 1),
            'required_time': self.REQUIRED_DURATION
        }
    
    def reset(self):
        """Reset timer for next event"""
        self.start_time = None
        self.elapsed_time = 0
        self.status = HygieneStatus.IDLE
        self.current_event = {}
    
    def log_event(self):
        """Log completed event to history"""
        if self.current_event:
            self.current_event['duration'] = self.elapsed_time
            self.current_event['end_time'] = time.time()
            self.current_event['status'] = 'completed' if self.status == HygieneStatus.COMPLETED else 'incomplete'
            self.event_log.append(self.current_event)
    
    def get_stats(self) -> Dict:
        """
        Get statistics from all logged events
        
        Returns:
            Dictionary with stats
        """
        if not self.event_log:
            return {
                'total_events': 0,
                'successful_events': 0,
                'failed_events': 0,
                'compliance_rate': 0,
                'avg_duration': 0
            }
        
        successful = sum(1 for e in self.event_log if e['status'] == 'completed')
        failed = len(self.event_log) - successful
        
        avg_duration = sum(e['duration'] for e in self.event_log) / len(self.event_log)
        
        return {
            'total_events': len(self.event_log),
            'successful_events': successful,
            'failed_events': failed,
            'compliance_rate': (successful / len(self.event_log) * 100) if self.event_log else 0,
            'avg_duration': round(avg_duration, 1)
        }
    
    def get_current_status(self) -> Dict:
        """Get current timer status"""
        return {
            'status': self.status.value,
            'elapsed_time': round(self.elapsed_time, 1),
            'required_time': self.REQUIRED_DURATION,
            'progress_percent': min(100, (self.elapsed_time / self.REQUIRED_DURATION) * 100)
        }


if __name__ == "__main__":
    print("Timer Logic module loaded successfully")
    print(f"WHO Standard Duration: {HygieneTimer.REQUIRED_DURATION} seconds")
