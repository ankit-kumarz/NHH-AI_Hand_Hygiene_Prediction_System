
print("[DEBUG] Entering ai/model.py", flush=True)
"""
Custom CNN Model for Hand Hygiene Detection
ResNet-based architecture with hand hygiene-specific optimizations
"""

print("[DEBUG] Importing tensorflow as tf", flush=True)
import tensorflow as tf
import keras
print("[DEBUG] Importing keras layers, models", flush=True)
from keras import layers, models
print("[DEBUG] Importing numpy as np", flush=True)
import numpy as np
print("[DEBUG] Importing PIL.Image", flush=True)
print("[DEBUG] Importing PIL.Image", flush=True)
from PIL import Image
print("[DEBUG] Importing json", flush=True)
import json
print("[DEBUG] Importing Path", flush=True)
from pathlib import Path
print("[DEBUG] Importing logging", flush=True)
import logging
print("[DEBUG] All imports DONE", flush=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HandHygieneModel:
    def __init__(self, model_name='hand_hygiene_detector'):
        self.model_name = model_name
        self.model_path = Path('ai/models')
        self.model_path.mkdir(parents=True, exist_ok=True)
        self.model = None
        self.history = None
    
    def build_model(self, input_shape=(224, 224, 3), num_classes=2):
        """
        Build custom CNN for hand hygiene detection
        backbone: Efficient net/ResNet50 with custom top layers
        """
        logger.info(f"Building CNN model with input shape {input_shape}...")
        
        # Use EfficientNetB0 pre-trained weights
        base_model = keras.applications.EfficientNetB0(
            input_shape=input_shape,
            include_top=False,
            weights='imagenet'
        )
        
        # Freeze base model layers
        base_model.trainable = False
        
        # Build custom top layers
        model = models.Sequential([
            # Input
            keras.Input(shape=input_shape),
            
            # Base model
            base_model,
            
            # Custom top layers
            layers.GlobalAveragePooling2D(),
            
            # Dense layers with regularization
            layers.Dense(512, activation='relu', name='dense1'),
            layers.BatchNormalization(),
            layers.Dropout(0.4),
            
            layers.Dense(256, activation='relu', name='dense2'),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            
            layers.Dense(128, activation='relu', name='dense3'),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            
            # Output layer (binary classification)
            layers.Dense(num_classes, activation='softmax', name='output')
        ])
        
        # Compile model
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=[
                keras.metrics.Accuracy(),
                keras.metrics.Precision(),
                keras.metrics.Recall(),
                keras.metrics.AUC()
            ]
        )
        
        self.model = model
        logger.info("Model built successfully!")
        logger.info(f"Total parameters: {model.count_params():,}")
        
        return model
    
    def unfreeze_base_model(self, num_layers_to_fine_tune=20):
        """Unfreeze last N layers of base model for fine-tuning"""
        logger.info(f"Unfreezing last {num_layers_to_fine_tune} layers for fine-tuning...")
        
        # Find the base model (EfficientNetB0 or ResNet50)
        base_model = None
        for layer in self.model.layers:
            if hasattr(layer, 'layers'):
                base_model = layer
                break
        
        if not base_model:
            logger.warning("Could not find base model to unfreeze. Skipping fine-tuning.")
            return

        base_model.trainable = True
        
        # Freeze all but last N layers
        for layer in base_model.layers[:-num_layers_to_fine_tune]:
            layer.trainable = False
        
        # Recompile with lower learning rate
        self.model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.00005),
            loss='categorical_crossentropy',
            metrics=['accuracy', keras.metrics.Precision(), keras.metrics.Recall()]
        )
        
        logger.info("Base model unfrozen for fine-tuning")
    
    def train(self, train_dataset, val_dataset, epochs=10, early_stopping=True):
        """Train the model"""
        logger.info("Starting model training...")
        
        callbacks = []
        
        if early_stopping:
            callbacks.append(
                keras.callbacks.EarlyStopping(
                    monitor='val_loss',
                    patience=5,
                    restore_best_weights=True,
                    verbose=1
                )
            )
        
        # Save best model
        callbacks.append(
            keras.callbacks.ModelCheckpoint(
                str(self.model_path / f'{self.model_name}_best.h5'),
                monitor='val_accuracy',
                save_best_only=True,
                verbose=1
            )
        )
        
        # Learning rate reduction
        callbacks.append(
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=3,
                min_lr=0.00001,
                verbose=1
            )
        )
        
        self.history = self.model.fit(
            train_dataset,
            validation_data=val_dataset,
            epochs=epochs,
            callbacks=callbacks,
            verbose=1
        )
        
        logger.info("Training complete!")
        return self.history
    
    def evaluate(self, test_dataset):
        """Evaluate model on test set"""
        logger.info("Evaluating model on test set...")
        
        metrics = self.model.evaluate(test_dataset, verbose=0)
        metric_names = self.model.metrics_names
        
        results = dict(zip(metric_names, metrics))
        
        logger.info("\n" + "="*50)
        logger.info("MODEL EVALUATION RESULTS")
        logger.info("="*50)
        
        for metric_name, value in results.items():
            logger.info(f"{metric_name}: {value:.4f}")
        
        return results
    
    def save_model(self):
        """Save trained model"""
        save_path = self.model_path / f'{self.model_name}_final.h5'
        self.model.save(str(save_path))
        logger.info(f"Model saved to {save_path}")
        
        # Save model config
        config_path = self.model_path / f'{self.model_name}_config.json'
        config = {
            'model_name': self.model_name,
            'input_shape': self.model.input_shape[1:],
            'num_classes': 2,
            'classes': ['no_activity', 'hand_washing']
        }
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Config saved to {config_path}")
    
    def load_model(self):
        """Load pre-trained model"""
        model_path = self.model_path / f'{self.model_name}_final.h5'
        
        if model_path.exists():
            self.model = keras.models.load_model(str(model_path))
            logger.info(f"Model loaded from {model_path}")
            return self.model
        else:
            logger.error(f"Model not found: {model_path}")
            return None
    
    def predict(self, image, return_confidence=True):
        """
        Predict on single image
        Returns: (class_name, confidence)
        """
        # Load image if string path provided
        if isinstance(image, str):
            image = Image.open(image).convert('RGB')
            image = image.resize((224, 224))
        
        # Convert to array
        img_array = np.array(image, dtype=np.float32)
        img_array = np.expand_dims(img_array, axis=0)
        
        # Predict
        predictions = self.model.predict(img_array, verbose=0)[0]
        
        class_names = ['no_activity', 'hand_washing']
        class_id = np.argmax(predictions)
        confidence = predictions[class_id]
        
        if return_confidence:
            return class_names[class_id], float(confidence)
        else:
            return class_names[class_id]
    
    def get_summary(self):
        """Print model summary"""
        if self.model:
            self.model.summary()
        else:
            logger.error("Model not built yet")

def create_dataset_pipeline(data_dir, batch_size=32, img_size=(224, 224)):
    """
    Create TensorFlow data pipeline
    """
    logger.info(f"Creating dataset pipeline from {data_dir}...")
    
    train_dir = Path(data_dir) / 'train'
    val_dir = Path(data_dir) / 'val'
    test_dir = Path(data_dir) / 'test'
    
    def load_and_augment(path, label):
        image = tf.io.read_file(path)
        image = tf.image.decode_jpeg(image, channels=3)
        image = tf.image.resize(image, img_size)
        
        # Data augmentation for training
        image = tf.image.random_flip_left_right(image)
        image = tf.image.random_brightness(image, 0.2)
        image = tf.image.random_contrast(image, 0.8, 1.2)
        
        return image, label
    
    def load_only(path, label):
        image = tf.io.read_file(path)
        image = tf.image.decode_jpeg(image, channels=3)
        image = tf.image.resize(image, img_size)
        return image, label
    
    # Load training data
    train_images = []
    train_labels = []
    
    for class_id, class_name in [(0, 'no_activity'), (1, 'hand_washing')]:
        class_dir = train_dir / class_name
        if class_dir.exists():
            for img_file in class_dir.glob('*'):
                train_images.append(str(img_file))
                train_labels.append(class_id)
    
    # Load validation data
    val_images = []
    val_labels = []
    
    for class_id, class_name in [(0, 'no_activity'), (1, 'hand_washing')]:
        class_dir = val_dir / class_name
        if class_dir.exists():
            for img_file in class_dir.glob('*'):
                val_images.append(str(img_file))
                val_labels.append(class_id)
    
    # Load test data
    test_images = []
    test_labels = []
    
    for class_id, class_name in [(0, 'no_activity'), (1, 'hand_washing')]:
        class_dir = test_dir / class_name
        if class_dir.exists():
            for img_file in class_dir.glob('*'):
                test_images.append(str(img_file))
                test_labels.append(class_id)
    
    # Convert to one-hot encoding
    train_labels = keras.utils.to_categorical(train_labels, num_classes=2)
    val_labels = keras.utils.to_categorical(val_labels, num_classes=2)
    test_labels = keras.utils.to_categorical(test_labels, num_classes=2)
    
    # Create datasets
    train_ds = tf.data.Dataset.from_tensor_slices((train_images, train_labels))
    train_ds = train_ds.map(load_and_augment).batch(batch_size).prefetch(tf.data.AUTOTUNE)
    
    val_ds = tf.data.Dataset.from_tensor_slices((val_images, val_labels))
    val_ds = val_ds.map(load_only).batch(batch_size).prefetch(tf.data.AUTOTUNE)
    
    test_ds = tf.data.Dataset.from_tensor_slices((test_images, test_labels))
    test_ds = test_ds.map(load_only).batch(batch_size).prefetch(tf.data.AUTOTUNE)
    
    logger.info(f"Dataset created:")
    logger.info(f"  Train: {len(train_images)} images")
    logger.info(f"  Val: {len(val_images)} images")
    logger.info(f"  Test: {len(test_images)} images")
    
    return train_ds, val_ds, test_ds

if __name__ == '__main__':
    # Example usage
    model = HandHygieneModel()
    model.build_model()
    model.get_summary()
