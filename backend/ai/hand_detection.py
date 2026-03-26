"""
Hand Detection Module using MediaPipe
Detects hands in real-time using MediaPipe Hands model
"""

import mediapipe as mp
import cv2
import numpy as np
from typing import Tuple, List, Dict


class HandDetector:
    """
    Hand detection using MediaPipe Hands
    Detects hand presence, position, and landmarks
    """
    
    def __init__(self, static_image_mode=False, max_num_hands=2, min_detection_confidence=0.7):
        """
        Initialize MediaPipe hand detector
        
        Args:
            static_image_mode: For static images or video
            max_num_hands: Max hands to detect (1 or 2)
            min_detection_confidence: Confidence threshold (0-1)
        """
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=static_image_mode,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence
        )
        self.hand_landmarks = None
        self.hand_handedness = None
        
    def detect_hands(self, frame: np.ndarray) -> Tuple[bool, np.ndarray]:
        """
        Detect hands in a frame
        
        Args:
            frame: Input video frame (BGR format)
            
        Returns:
            Tuple of:
            - hands_detected (bool): Whether hands were detected
            - frame_with_landmarks (np.ndarray): Frame with drawn landmarks
        """
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        frame_copy = frame.copy()
        hands_detected = False
        
        if results.multi_hand_landmarks and results.multi_handedness:
            hands_detected = True
            self.hand_landmarks = results.multi_hand_landmarks
            self.hand_handedness = results.multi_handedness
            
            # Draw landmarks on frame
            for hand_landmarks, handedness in zip(
                results.multi_hand_landmarks, 
                results.multi_handedness
            ):
                self.mp_drawing.draw_landmarks(
                    frame_copy,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS
                )
        else:
            self.hand_landmarks = None
            self.hand_handedness = None
        
        return hands_detected, frame_copy
    
    def get_hand_center(self, landmarks) -> Tuple[int, int]:
        """
        Calculate center point of hand from landmarks
        
        Args:
            landmarks: Hand landmarks from MediaPipe
            
        Returns:
            (x, y) center coordinates
        """
        x_coords = [lm.x for lm in landmarks.landmark]
        y_coords = [lm.y for lm in landmarks.landmark]
        
        center_x = int((min(x_coords) + max(x_coords)) / 2)
        center_y = int((min(y_coords) + max(y_coords)) / 2)
        
        return center_x, center_y
    
    def get_hand_bounding_box(self, landmarks) -> Tuple[int, int, int, int]:
        """
        Get bounding box around detected hand
        
        Args:
            landmarks: Hand landmarks from MediaPipe
            
        Returns:
            (x1, y1, x2, y2) bounding box coordinates
        """
        x_coords = [lm.x for lm in landmarks.landmark]
        y_coords = [lm.y for lm in landmarks.landmark]
        
        x1 = int(min(x_coords) * 100)  # Will be multiplied by frame width
        y1 = int(min(y_coords) * 100)
        x2 = int(max(x_coords) * 100)
        y2 = int(max(y_coords) * 100)
        
        return x1, y1, x2, y2
    
    def draw_hand_info(self, frame: np.ndarray, hand_count: int) -> np.ndarray:
        """
        Draw hand count and info on frame
        
        Args:
            frame: Video frame
            hand_count: Number of hands detected
            
        Returns:
            Frame with drawn info
        """
        frame_copy = frame.copy()
        h, w, _ = frame.shape
        
        # Display hand count
        text = f"Hands Detected: {hand_count}"
        color = (0, 255, 0) if hand_count > 0 else (0, 0, 255)
        
        cv2.putText(
            frame_copy,
            text,
            (w - 300, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            color,
            2
        )
        
        return frame_copy
    
    def release(self):
        """Release resources"""
        self.hands.close()


if __name__ == "__main__":
    print("Hand Detector module loaded successfully")
    print("Use this module in timer_logic.py")
