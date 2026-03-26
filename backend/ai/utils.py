"""
Utility functions for Hand Hygiene Detection System
"""

import cv2
import numpy as np
from typing import Tuple


def draw_status_display(frame: np.ndarray, timer_data: dict) -> np.ndarray:
    """
    Draw status, timer, and progress on frame
    
    Args:
        frame: Video frame
        timer_data: Dictionary with status info
        
    Returns:
        Frame with drawn status
    """
    frame_copy = frame.copy()
    h, w, _ = frame.shape
    
    status = timer_data.get('status', 'Idle')
    elapsed = timer_data.get('elapsed_time', 0)
    required = timer_data.get('required_time', 20)
    progress = timer_data.get('progress_percent', 0)
    
    # Determine color based on status
    if status == "Completed ✓":
        color = (0, 255, 0)  # Green
        bg_color = (0, 200, 0)
    elif status == "Failed ✗":
        color = (0, 0, 255)  # Red
        bg_color = (0, 0, 200)
    elif status == "Washing":
        color = (0, 165, 255)  # Orange
        bg_color = (0, 140, 255)
    elif status == "Detected":
        color = (0, 255, 255)  # Yellow
        bg_color = (0, 200, 200)
    else:
        color = (100, 100, 100)  # Gray
        bg_color = (80, 80, 80)
    
    # Draw background rectangle for status
    cv2.rectangle(frame_copy, (10, 10), (400, 120), bg_color, -1)
    cv2.rectangle(frame_copy, (10, 10), (400, 120), color, 2)
    
    # Status text
    cv2.putText(
        frame_copy,
        f"Status: {status}",
        (30, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.2,
        (255, 255, 255),
        2
    )
    
    # Timer text
    cv2.putText(
        frame_copy,
        f"Time: {elapsed:.1f}s / {required}s",
        (30, 90),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (255, 255, 255),
        2
    )
    
    # Draw progress bar
    bar_width = 300
    bar_height = 30
    bar_x = w - bar_width - 20
    bar_y = 20
    
    # Background bar
    cv2.rectangle(
        frame_copy,
        (bar_x, bar_y),
        (bar_x + bar_width, bar_y + bar_height),
        (50, 50, 50),
        -1
    )
    
    # Progress bar
    progress_width = int(bar_width * (progress / 100))
    cv2.rectangle(
        frame_copy,
        (bar_x, bar_y),
        (bar_x + progress_width, bar_y + bar_height),
        color,
        -1
    )
    
    # Border
    cv2.rectangle(
        frame_copy,
        (bar_x, bar_y),
        (bar_x + bar_width, bar_y + bar_height),
        (255, 255, 255),
        2
    )
    
    # Progress percentage
    cv2.putText(
        frame_copy,
        f"{int(progress)}%",
        (bar_x + 120, bar_y + 22),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )
    
    return frame_copy


def draw_instructions(frame: np.ndarray) -> np.ndarray:
    """
    Draw instructions on frame
    
    Args:
        frame: Video frame
        
    Returns:
        Frame with instructions
    """
    frame_copy = frame.copy()
    h, w, _ = frame.shape
    
    # Semi-transparent overlay
    overlay = frame_copy.copy()
    cv2.rectangle(overlay, (10, h - 150), (w - 10, h - 10), (0, 0, 0), -1)
    frame_copy = cv2.addWeighted(overlay, 0.3, frame_copy, 0.7, 0)
    
    # Instructions
    instructions = [
        "WHO Hand Hygiene Protocol: Wash hands for 20 seconds",
        "1. Show hands to camera | 2. Perform handwashing",
        "3. Hold for 20 seconds | 4. System logs when complete"
    ]
    
    y_pos = h - 120
    for i, instruction in enumerate(instructions):
        cv2.putText(
            frame_copy,
            instruction,
            (30, y_pos + (i * 35)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            1
        )
    
    return frame_copy


def draw_fps(frame: np.ndarray, fps: float) -> np.ndarray:
    """
    Draw FPS counter on frame
    
    Args:
        frame: Video frame
        fps: Frames per second
        
    Returns:
        Frame with FPS counter
    """
    cv2.putText(
        frame,
        f"FPS: {fps:.1f}",
        (10, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 0),
        1
    )
    return frame


def display_alert_message(frame: np.ndarray, message: str, color: Tuple) -> np.ndarray:
    """
    Display alert message on frame
    
    Args:
        frame: Video frame
        message: Alert message
        color: RGB color tuple
        
    Returns:
        Frame with alert
    """
    frame_copy = frame.copy()
    h, w, _ = frame.shape
    
    # Alert box
    text_size = cv2.getTextSize(message, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
    box_w = text_size[0] + 20
    box_h = text_size[1] + 20
    box_x = (w - box_w) // 2
    box_y = (h - box_h) // 2
    
    # Draw alert box
    cv2.rectangle(frame_copy, (box_x, box_y), (box_x + box_w, box_y + box_h), color, -1)
    cv2.rectangle(frame_copy, (box_x, box_y), (box_x + box_w, box_y + box_h), (255, 255, 255), 3)
    
    # Draw message
    text_x = box_x + 10
    text_y = box_y + text_size[1] + 10
    cv2.putText(frame_copy, message, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    return frame_copy


if __name__ == "__main__":
    print("Utility functions module loaded successfully")
