"""
Integration module for Phase 1 AI Detection with Phase 2 Backend
Sends hand hygiene events from detector to Flask API
"""

import requests
import json
from typing import Dict, Optional


class HygieneAPIClient:
    """
    Client for communicating with the Flask backend API
    Sends detection results to database
    """
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        """
        Initialize API client
        
        Args:
            base_url: Flask backend URL
        """
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.connected = False
        self.check_connection()
    
    def check_connection(self) -> bool:
        """Check if backend is available"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            self.connected = response.status_code == 200
            return self.connected
        except Exception as e:
            print(f"⚠️ Backend not available: {e}")
            self.connected = False
            return False
    
    def log_event(self, 
                  duration: float, 
                  status: str,
                  user_id: str = "system",
                  location: Optional[str] = None,
                  department: Optional[str] = None) -> bool:
        """
        Log hygiene event to backend
        
        Args:
            duration: Event duration in seconds
            status: 'completed' or 'incomplete'
            user_id: User identifier
            location: Physical location
            department: Department name
            
        Returns:
            True if successful
        """
        if not self.connected:
            print("⚠️ Not connected to backend")
            return False
        
        try:
            payload = {
                "user_id": user_id,
                "duration": round(duration, 1),
                "status": status,
                "location": location,
                "department": department
            }
            
            response = requests.post(
                f"{self.api_url}/log",
                json=payload,
                timeout=5
            )
            
            if response.status_code == 201:
                return True
            else:
                print(f"❌ Failed to log event: {response.text}")
                return False
        
        except Exception as e:
            print(f"❌ Error logging event: {e}")
            return False
    
    def get_stats(self, days: int = 7, user_id: Optional[str] = None) -> Dict:
        """
        Get statistics from backend
        
        Args:
            days: Number of days to retrieve
            user_id: Optional user filter
            
        Returns:
            Statistics dictionary
        """
        if not self.connected:
            return {}
        
        try:
            params = {'days': days}
            if user_id:
                params['user_id'] = user_id
            
            response = requests.get(
                f"{self.api_url}/stats",
                params=params,
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {}
        
        except Exception as e:
            print(f"❌ Error getting stats: {e}")
            return {}


if __name__ == "__main__":
    print("Integration module loaded")
