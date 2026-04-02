"""
Real-time Hand Hygiene Detection Engine
Uses trained model with webcam for live detection and accuracy tracking
"""

import cv2
import numpy as np
import tensorflow as tf
from pathlib import Path
import json
import time
from collections import deque
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HandHygieneInferenceEngine:
    def __init__(self, model_path='ai/models/hand_hygiene_detector_final.h5'):
        self.model_path = Path(model_path)
        self.model = None
        self.config = None
        
        # Performance tracking
        self.frame_times = deque(maxlen=30)  # Last 30 frames
        self.detections = deque(maxlen=100)  # Last 100 detections
        self.predictions = deque(maxlen=100)
        
        # Accuracy metrics
        self.accuracy_tracker = {
            'total_frames': 0,
            'detections': 0,
            'hand_washing': 0,
            'no_activity': 0,
            'confidences': []
        }
        
        self.load_model()
    
    def load_model(self):
        """Load trained model and config"""
        if not self.model_path.exists():
            logger.error(f"Model not found: {self.model_path}")
            logger.info("Please run ai/train.py first to train the model")
            return False
        
        try:
            self.model = tf.keras.models.load_model(str(self.model_path))
            logger.info(f"Model loaded: {self.model_path}")
            
            # Load config
            config_path = self.model_path.parent / f"{self.model_path.stem.replace('_final', '')}_config.json"
            if config_path.exists():
                with open(config_path) as f:
                    self.config = json.load(f)
                logger.info(f"Config loaded: {self.config}")
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
    
    def preprocess_frame(self, frame):
        """Preprocess webcam frame for model"""
        # Resize to model input size
        frame_resized = cv2.resize(frame, (224, 224))
        
        # Normalize
        frame_normalized = frame_resized / 255.0
        
        # Add batch dimension
        frame_batch = np.expand_dims(frame_normalized, axis=0)
        
        return frame_batch
    
    def predict(self, frame):
        """
        Run inference on frame
        Returns: (class_name, confidence, processing_time)
        """
        start_time = time.time()
        
        try:
            # Preprocess
            frame_batch = self.preprocess_frame(frame)
            
            # Predict
            predictions = self.model.predict(frame_batch, verbose=0)[0]
            
            # Get results
            class_names = self.config['classes'] if self.config else ['no_activity', 'hand_washing']
            class_id = np.argmax(predictions)
            confidence = float(predictions[class_id])
            
            processing_time = time.time() - start_time
            
            return {
                'class': class_names[class_id],
                'class_id': int(class_id),
                'confidence': confidence,
                'all_scores': {class_names[i]: float(predictions[i]) for i in range(len(class_names))},
                'processing_time': processing_time
            }
        
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return None
    
    def run_webcam_detection(self, confidence_threshold=0.7, duration=60):
        """
        Run real-time hand hygiene detection on webcam
        
        Args:
            confidence_threshold: Minimum confidence to count as detection
            duration: How long to run (seconds)
        """
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            logger.error("Cannot open webcam!")
            return False
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        logger.info("Starting webcam detection...")
        logger.info("Press 'q' to quit, 's' to save screenshot, 'r' to reset metrics")
        logger.info(f"Confidence threshold: {confidence_threshold}")
        
        start_time = time.time()
        frame_count = 0
        
        try:
            while (time.time() - start_time) < duration:
                ret, frame = cap.read()
                
                if not ret:
                    logger.warning("Failed to read frame")
                    break
                
                frame_count += 1
                frame_time = time.time()
                
                # Flip for selfie view
                frame = cv2.flip(frame, 1)
                h, w, c = frame.shape
                
                # Run prediction
                prediction = self.predict(frame)
                
                if prediction:
                    # Track metrics
                    self.accuracy_tracker['total_frames'] += 1
                    self.accuracy_tracker['confidences'].append(prediction['confidence'])
                    
                    if prediction['confidence'] >= confidence_threshold:
                        self.accuracy_tracker['detections'] += 1
                        self.accuracy_tracker[prediction['class']] += 1
                    
                    self.predictions.append({
                        'timestamp': datetime.now().isoformat(),
                        'class': prediction['class'],
                        'confidence': prediction['confidence'],
                        'processing_time': prediction['processing_time']
                    })
                    
                    # Calculate FPS
                    self.frame_times.append(prediction['processing_time'])
                    avg_frame_time = np.mean(self.frame_times) if self.frame_times else 0
                    fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
                    
                    # Draw results on frame
                    color = (0, 255, 0) if prediction['class'] == 'hand_washing' else (0, 165, 255)
                    thickness = 2
                    
                    # Detection box
                    cv2.rectangle(frame, (10, 10), (400, 100), color, thickness)
                    
                    # Class label
                    cv2.putText(frame, f"Class: {prediction['class']}", (20, 40),
                               cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                    
                    # Confidence
                    cv2.putText(frame, f"Confidence: {prediction['confidence']:.2%}", (20, 70),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                    
                    # FPS
                    cv2.putText(frame, f"FPS: {fps:.1f}", (20, 100),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                    
                    # Elapsed time
                    elapsed = int(time.time() - start_time)
                    cv2.putText(frame, f"Time: {elapsed}s", (w-150, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                    
                    # Detection stats
                    detection_rate = (self.accuracy_tracker['detections'] / 
                                    self.accuracy_tracker['total_frames'] * 100 
                                    if self.accuracy_tracker['total_frames'] > 0 else 0)
                    
                    cv2.putText(frame, f"Detection Rate: {detection_rate:.1f}%", (w-250, 60),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                    
                    cv2.putText(frame, f"Avg Confidence: {np.mean(self.accuracy_tracker['confidences']):.2%}", 
                               (w-250, 90),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                
                # Display frame
                cv2.imshow('Hand Hygiene Detection (Production Model)', frame)
                
                # Handle keys
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    logger.info("Stopping detection...")
                    break
                elif key == ord('s'):
                    filename = f"detections/detection_{int(time.time())}.jpg"
                    Path('detections').mkdir(exist_ok=True)
                    cv2.imwrite(filename, frame)
                    logger.info(f"Screenshot saved: {filename}")
                elif key == ord('r'):
                    logger.info("Resetting metrics...")
                    self.accuracy_tracker = {
                        'total_frames': 0,
                        'detections': 0,
                        'hand_washing': 0,
                        'no_activity': 0,
                        'confidences': []
                    }
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
            
            # Print final report
            self.print_report()
    
    def print_report(self):
        """Print accuracy and performance report"""
        logger.info("\n" + "="*70)
        logger.info("HAND HYGIENE DETECTION - PERFORMANCE REPORT")
        logger.info("="*70)
        
        total_frames = self.accuracy_tracker['total_frames']
        
        if total_frames == 0:
            logger.info("No frames processed")
            return
        
        # Detection statistics
        logger.info("\n📊 DETECTION STATISTICS")
        logger.info("-" * 70)
        logger.info(f"Total Frames: {total_frames}")
        logger.info(f"Detections: {self.accuracy_tracker['detections']}")
        logger.info(f"Detection Rate: {self.accuracy_tracker['detections']/total_frames*100:.2f}%")
        
        logger.info(f"\nClass Distribution:")
        logger.info(f"  Hand Washing: {self.accuracy_tracker['hand_washing']} ({self.accuracy_tracker['hand_washing']/self.accuracy_tracker['detections']*100 if self.accuracy_tracker['detections'] > 0 else 0:.2f}%)")
        logger.info(f"  No Activity: {self.accuracy_tracker['no_activity']} ({self.accuracy_tracker['no_activity']/self.accuracy_tracker['detections']*100 if self.accuracy_tracker['detections'] > 0 else 0:.2f}%)")
        
        # Confidence statistics
        logger.info("\n🎯 CONFIDENCE STATISTICS")
        logger.info("-" * 70)
        
        if self.accuracy_tracker['confidences']:
            confidences = np.array(self.accuracy_tracker['confidences'])
            logger.info(f"Mean Confidence: {np.mean(confidences):.4f}")
            logger.info(f"Std Deviation: {np.std(confidences):.4f}")
            logger.info(f"Min Confidence: {np.min(confidences):.4f}")
            logger.info(f"Max Confidence: {np.max(confidences):.4f}")
        
        # Performance metrics
        logger.info("\n⚡ PERFORMANCE METRICS")
        logger.info("-" * 70)
        
        if self.frame_times:
            frame_times = np.array(list(self.frame_times)) * 1000  # Convert to ms
            fps = 1000 / np.mean(frame_times)
            logger.info(f"Average FPS: {fps:.2f}")
            logger.info(f"Average Frame Processing Time: {np.mean(frame_times):.2f}ms")
            logger.info(f"Min Processing Time: {np.min(frame_times):.2f}ms")
            logger.info(f"Max Processing Time: {np.max(frame_times):.2f}ms")
        
        logger.info("\n" + "="*70)

def main():
    logger.info("Initializing Hand Hygiene Detection Engine...")
    
    engine = HandHygieneInferenceEngine()
    
    if engine.model is None:
        logger.error("Model not loaded. Cannot proceed with detection.")
        return
    
    logger.info("✅ Model loaded successfully!")
    logger.info("\nStarting real-time detection on webcam...")
    
    engine.run_webcam_detection(confidence_threshold=0.7, duration=300)  # 5 minutes

if __name__ == '__main__':
    main()
