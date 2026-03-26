"""
PHASE 1: AI HAND HYGIENE DETECTION SYSTEM
Complete working prototype with real-time hand detection
and WHO 20-second compliance monitoring

Usage:
    python detect_hygiene.py
    
Press 'q' to quit
Press 's' to save screenshot
"""

import cv2
import sys
import time
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai.hand_detection import HandDetector
from ai.timer_logic import HygieneTimer
from ai.utils import (
    draw_status_display,
    draw_instructions,
    draw_fps,
    display_alert_message
)


class HygieneMonitor:
    """
    Real-time Hand Hygiene Monitoring System
    Integrates hand detection with timer and status tracking
    """
    
    def __init__(self, camera_index=0):
        """
        Initialize monitoring system
        
        Args:
            camera_index: Webcam index (0 = default)
        """
        print("🏥 Initializing Hand Hygiene Detection System...")
        
        # Initialize hand detector
        self.detector = HandDetector(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7
        )
        
        # Initialize timer
        self.timer = HygieneTimer()
        
        # Initialize camera
        self.cap = cv2.VideoCapture(camera_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Check camera
        if not self.cap.isOpened():
            raise RuntimeError("❌ Failed to open camera. Check camera connection.")
        
        print("✅ Hand Detector initialized")
        print("✅ Timer system initialized")
        print("✅ Camera ready")
        print()
        print("=" * 70)
        print("🎯 WHO Hand Hygiene Protocol:")
        print("   • Effective handwashing requires 20 seconds")
        print("   • Status will change: Idle → Detected → Washing → Completed")
        print("=" * 70)
        
        # Performance tracking
        self.prev_frame_time = 0
        self.current_frame_time = 0
        self.fps = 0
        self.frame_count = 0
        
        # Event tracking for alerts
        self.last_alert_time = 0
        self.alert_cooldown = 2  # seconds
        self.prev_status = None
    
    def show_alert(self, frame, message, is_success=False):
        """Show alert message"""
        color = (0, 255, 0) if is_success else (0, 0, 255)
        return display_alert_message(frame, message, color)
    
    def run(self):
        """Main detection loop"""
        print("🎥 Starting real-time monitoring...")
        print("Press 'q' to quit | 's' to save screenshot\n")
        
        frame_count = 0
        
        while True:
            ret, frame = self.cap.read()
            
            if not ret:
                print("❌ Failed to read frame")
                break
            
            frame_count += 1
            
            # Flip frame for mirror effect
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            
            # ============ AI DETECTION ============
            hands_detected, frame_with_landmarks = self.detector.detect_hands(frame)
            
            # ============ TIMER UPDATE ============
            timer_status = self.timer.update_timer(hands_detected)
            
            # ============ DISPLAY UPDATES ============
            
            # 1. Draw landmarks
            display_frame = frame_with_landmarks.copy()
            
            # 2. Draw status display
            display_frame = draw_status_display(display_frame, timer_status)
            
            # 3. Draw instructions
            display_frame = draw_instructions(display_frame)
            
            # 4. Calculate and draw FPS
            self.current_frame_time = time.time()
            self.fps = 1 / (self.current_frame_time - self.prev_frame_time + 0.0001)
            self.prev_frame_time = self.current_frame_time
            display_frame = draw_fps(display_frame, self.fps)
            
            # 5. Show status change alerts
            current_status = timer_status['status']
            if current_status != self.prev_status and time.time() - self.last_alert_time > self.alert_cooldown:
                if current_status == "Detected":
                    display_frame = self.show_alert(display_frame, "👋 Hands Detected!", False)
                elif current_status == "Washing":
                    display_frame = self.show_alert(display_frame, "🧼 Washing...", False)
                elif current_status == "Completed ✓":
                    display_frame = self.show_alert(display_frame, "✅ Washing Complete!", True)
                    print("✅ Event Completed: 20-second handwash successful!")
                elif current_status == "Failed ✗":
                    display_frame = self.show_alert(display_frame, "⚠️ Insufficient Time", False)
                    print("⚠️ Event Failed: Hands removed before 20 seconds")
                
                self.last_alert_time = time.time()
            
            self.prev_status = current_status
            
            # ============ DISPLAY FRAME ============
            cv2.imshow("🏥 Hand Hygiene Monitoring System", display_frame)
            
            # ============ KEYBOARD INPUT ============
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                print("\n🛑 Shutting down...")
                break
            
            elif key == ord('s'):
                filename = f"screenshot_{int(time.time())}.png"
                cv2.imwrite(filename, display_frame)
                print(f"📸 Screenshot saved: {filename}")
            
            # Print stats every 30 frames
            if frame_count % 30 == 0:
                stats = self.timer.get_stats()
                print(f"\n📊 Running Stats (Frame {frame_count}):")
                print(f"   Total Events: {stats['total_events']}")
                print(f"   Successful: {stats['successful_events']}")
                print(f"   Failed: {stats['failed_events']}")
                print(f"   Compliance Rate: {stats['compliance_rate']:.1f}%")
                print(f"   Avg Duration: {stats['avg_duration']:.1f}s")
        
        # Cleanup
        self.cleanup()
    
    def cleanup(self):
        """Release resources"""
        print("\n🧹 Cleaning up...")
        self.detector.release()
        self.cap.release()
        cv2.destroyAllWindows()
        
        # Final stats
        final_stats = self.timer.get_stats()
        print("\n" + "=" * 70)
        print("📈 FINAL SESSION STATISTICS:")
        print("=" * 70)
        print(f"Total Hand Hygiene Events: {final_stats['total_events']}")
        print(f"Successful Events (≥20s): {final_stats['successful_events']}")
        print(f"Incomplete Events (<20s): {final_stats['failed_events']}")
        print(f"Overall Compliance Rate: {final_stats['compliance_rate']:.1f}%")
        print(f"Average Wash Duration: {final_stats['avg_duration']:.1f}s")
        print("=" * 70)
        print("✅ Session ended successfully!")


def main():
    """Main entry point"""
    try:
        monitor = HygieneMonitor(camera_index=0)
        monitor.run()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
