"""
Backend integration for AI Hand Hygiene Model
Flask API endpoints for real-time model predictions
"""

import cv2
import numpy as np
import json
from pathlib import Path
from datetime import datetime
import threading
import queue
import time
import logging

# TensorFlow
import tensorflow as tf
from tensorflow import keras

logger = logging.getLogger(__name__)

class ModelService:
    """Singleton service for managing AI model"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.model = None
        self.config = None
        self.metrics = {
            'total_predictions': 0,
            'hand_washing_count': 0,
            'no_activity_count': 0,
            'avg_confidence': 0.0,
            'predictions_history': []
        }
        
        self.load_model()
        self._initialized = True
    
    def load_model(self):
        """Load trained model"""
        # Look in project root relative to this file
        root_dir = Path(__file__).parent.parent
        model_path = root_dir / 'ai/models/hand_hygiene_detector_final.h5'
        
        if not model_path.exists():
            # Fallback for current working directory
            model_path = Path('ai/models/hand_hygiene_detector_final.h5')
            
        if not model_path.exists():
            logger.warning(f"Model not found at: {model_path.absolute()}")
            return False
        
        try:
            self.model = keras.models.load_model(str(model_path))
            
            # Load config
            config_path = model_path.parent / 'hand_hygiene_detector_config.json'
            if config_path.exists():
                with open(config_path) as f:
                    self.config = json.load(f)
            
            logger.info("✅ Model loaded successfully")
            return True
        
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
    
    def predict(self, frame):
        """
        Predict on frame
        Returns dict with prediction and metrics
        """
        if self.model is None:
            return None
        
        try:
            # Preprocess
            frame_resized = cv2.resize(frame, (224, 224))
            frame_normalized = frame_resized / 255.0
            frame_batch = np.expand_dims(frame_normalized, axis=0)
            
            # Predict
            predictions = self.model.predict(frame_batch, verbose=0)[0]
            
            class_names = self.config['classes'] if self.config else ['no_activity', 'hand_washing']
            class_id = np.argmax(predictions)
            confidence = float(predictions[class_id])
            
            # Update metrics
            self.metrics['total_predictions'] += 1
            if class_id == 1:
                self.metrics['hand_washing_count'] += 1
            else:
                self.metrics['no_activity_count'] += 1
            
            self.metrics['predictions_history'].append({
                'timestamp': datetime.now().isoformat(),
                'class': class_names[class_id],
                'confidence': confidence
            })
            
            # Keep only last 100 predictions
            if len(self.metrics['predictions_history']) > 100:
                self.metrics['predictions_history'] = self.metrics['predictions_history'][-100:]
            
            # Calculate average confidence
            confidences = [p['confidence'] for p in self.metrics['predictions_history']]
            self.metrics['avg_confidence'] = float(np.mean(confidences))
            
            return {
                'class': class_names[class_id],
                'confidence': confidence,
                'all_scores': {class_names[i]: float(predictions[i]) for i in range(len(class_names))},
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return None
    
    def get_metrics(self):
        """Get current model metrics"""
        total = self.metrics['total_predictions']
        
        return {
            'total_predictions': total,
            'hand_washing_detected': self.metrics['hand_washing_count'],
            'no_activity_detected': self.metrics['no_activity_count'],
            'hand_washing_rate': (self.metrics['hand_washing_count'] / total * 100 
                                 if total > 0 else 0),
            'average_confidence': self.metrics['avg_confidence'],
            'recent_predictions': self.metrics['predictions_history'][-10:]
        }
    
    def reset_metrics(self):
        """Reset metrics"""
        self.metrics = {
            'total_predictions': 0,
            'hand_washing_count': 0,
            'no_activity_count': 0,
            'avg_confidence': 0.0,
            'predictions_history': []
        }
        logger.info("Metrics reset")

# Initialize global model service
model_service = None

def init_model_service():
    """Initialize model service (call from Flask app)"""
    global model_service
    model_service = ModelService()
    return model_service

def get_model_service():
    """Get model service instance"""
    global model_service
    if model_service is None:
        model_service = ModelService()
    return model_service
