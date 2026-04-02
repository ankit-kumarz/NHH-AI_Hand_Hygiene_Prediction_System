"""
PHASE 2: DOCTOR IDENTITY VERIFICATION & ACCESS CONTROL
Uses MediaPipe Face Detection to identify personnel and 
triggers audio alerts + database logging.
"""

import cv2
import mediapipe as mp
import time
import winsound
import requests
import json
from pathlib import Path

class AccessControlSystem:
    def __init__(self):
        print("👤 Initializing Face Identity Verification & Access Control...")
        
        # MediaPipe Face Detection
        self.mp_face = mp.solutions.face_detection
        self.mp_drawing = mp.solutions.drawing_utils
        self.face_detection = self.mp_face.FaceDetection(
            model_selection=0, # 0 for short-range (within 2m)
            min_detection_confidence=0.75
        )
        
        # Audio Alert Settings (Beeps)
        # winsound.Beep(frequency, duration)
        self.BEEP_START = (1000, 200)   # Frequency 1000Hz, 200ms
        self.BEEP_SUCCESS = (1800, 400) # Higher tone for success
        self.BEEP_FAIL = (400, 800)     # Low tone for warning
        
        # Identity Status
        self.identified_user = "Searching..."
        self.identified_id = None
        self.is_person_detected = False
        self.last_beep_time = 0
        
        # Backend Config
        self.api_url = "http://localhost:5000/api"
        
    def trigger_beep(self, type="start"):
        """Triggers a physical motherboard beep"""
        try:
            if type == "start":
                winsound.Beep(*self.BEEP_START)
            elif type == "success":
                winsound.Beep(*self.BEEP_SUCCESS)
            elif type == "fail":
                winsound.Beep(*self.BEEP_FAIL)
        except Exception as e:
            print(f"Beep failed: {e}")

    def report_event(self, user_id, status, duration=0):
        """Sends data to Flask backend for live dashboard monitoring"""
        try:
            # Map simplified status to backend endpoints
            if status == "detected":
                # Check for access (this will log to access_logs)
                payload = {
                    "employee_id": user_id,
                    "gate_id": "icu_main"
                }
                response = requests.post(f"{self.api_url}/access/request", json=payload, timeout=2)
                
                if response.status_code == 200:
                    result = response.json().get('access', {})
                    if result.get('access_granted'):
                        print(f"✅ ACCESS GRANTED: User {user_id}")
                        self.trigger_beep("success")
                    else:
                        print(f"❌ ACCESS DENIED: {user_id} - Reason: {result.get('denial_reason')}")
                        self.trigger_beep("fail")
            
            elif status == "violation":
                # Log a manual alert for non-compliance entry attempts
                payload = {
                    "employee_id": user_id,
                    "alert_type": "ACCESS_VIOLATION",
                    "message": f"Personnel {user_id} attempted entry without proper hand hygiene."
                }
                response = requests.post(f"{self.api_url}/alerts", json=payload, timeout=2)
                
                if response.status_code == 201:
                    print(f"🚨 VIOLATION ALERT SENT: {user_id}")
            
        except Exception as e:
            print(f"⚠️ Dashboard update failed (is backend running?): {e}")

    def process_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_detection.process(rgb_frame)
        
        self.is_person_detected = False
        
        if results.detections:
            self.is_person_detected = True
            for detection in results.detections:
                # Draw face bounding box
                self.mp_drawing.draw_detection(frame, detection)
                
                # SIMULATED FACE RECOGNITION (Doctor A)
                # In a real scenario, we compare the face embedding here
                if self.identified_id is None:
                    self.identified_user = "Dr. Smith (ID: 7041)"
                    self.identified_id = "DR7041"
                    
                    # Beep and Notify Dashboard
                    self.trigger_beep("start")
                    self.report_event(self.identified_id, "detected")
        else:
            if self.identified_id is not None:
                # Reset when person leaves
                self.identified_user = "Searching..."
                self.identified_id = None

        return frame

def main():
    system = AccessControlSystem()
    cap = cv2.VideoCapture(0)
    
    print("🎥 Access Control Camera Active.")
    print("Press q to quit | v to simulate violation (doctor enters without wash)")
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        
        frame = cv2.flip(frame, 1) # Mirror view
        frame = system.process_frame(frame)
        
        # UI DISPLAY
        color = (0, 255, 0) if system.is_person_detected else (0, 0, 255)
        cv2.rectangle(frame, (10, 10), (500, 110), (0, 0, 0), -1) # Header box
        
        cv2.putText(frame, "ICU GATE STATUS: " + ("LOCKED" if not system.is_person_detected else "ACCESS PENDING"), 
                    (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        if system.is_person_detected:
            cv2.putText(frame, "PERSONNEL: " + system.identified_user, 
                        (20, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
        cv2.imshow("ICU Gate Access Control - Face Verification", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        elif key == ord("v"): # Manual Violation Trigger for Testing
            if system.identified_id:
                system.report_event(system.identified_id, "violation")
                system.trigger_beep("fail")
                print("❌ VIOLATION RECORDED for " + system.identified_id)
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          