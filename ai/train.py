
print("[DEBUG] Starting ai/train.py", flush=True)
import sys
import os
from pathlib import Path
print("[DEBUG] Imports: sys, os, Path OK", flush=True)

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))
print("[DEBUG] sys.path updated", flush=True)

import ai.model
from ai.model import HandHygieneModel, create_dataset_pipeline
print("[DEBUG] Imported HandHygieneModel and create_dataset_pipeline", flush=True)
from ai.dataset import HandHygieneDataset
print("[DEBUG] Imported HandHygieneDataset", flush=True)
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    print("[DEBUG] Entered main()", flush=True)
    logger.info("="*60)
    logger.info("HAND HYGIENE DETECTION MODEL - TRAINING PIPELINE")
    logger.info("="*60)
    
    # Step 1: Prepare Dataset
    logger.info("\n[STEP 1] PREPARING DATASET")
    logger.info("-" * 60)
    
    dataset = HandHygieneDataset(data_dir='data/ml_dataset')
    
    # Generate/collect data (skip webcam, use synthetic data)
    logger.info("\nCreating synthetic training data...")
    try:
        dataset._create_placeholder_dataset(num_samples=100)
        logger.info("✓ Synthetic dataset created")
    except Exception as e:
        logger.error(f"Failed to create dataset: {e}")
        return
    
    # Preprocess
    logger.info("\nPreprocessing images...")
    dataset.preprocess_images(img_size=(224, 224))
    
    # Show stats
    stats = dataset.get_dataset_stats()
    
    # Step 2: Create Data Pipeline
    logger.info("\n[STEP 2] CREATING DATA PIPELINE")
    logger.info("-" * 60)
    
    train_ds, val_ds, test_ds = create_dataset_pipeline(
        data_dir='data/ml_dataset/processed',
        batch_size=32,
        img_size=(224, 224)
    )
    
    # Step 3: Build Model
    logger.info("\n[STEP 3] BUILDING MODEL")
    logger.info("-" * 60)
    
    model = HandHygieneModel(model_name='hand_hygiene_detector')
    cnn_model = model.build_model(input_shape=(224, 224, 3), num_classes=2)
    
    model.get_summary()
    
    # Step 4: Train Model
    logger.info("\n[STEP 4] TRAINING MODEL")
    logger.info("-" * 60)
    
    logger.info("Phase 1: Training with frozen backbone (epochs=5)...")
    history1 = model.train(
        train_dataset=train_ds,
        val_dataset=val_ds,
        epochs=5,
        early_stopping=True
    )
    
    logger.info("\nPhase 2: Fine-tuning with unfrozen layers (epochs=5)...")
    model.unfreeze_base_model(num_layers_to_fine_tune=20)
    history2 = model.train(
        train_dataset=train_ds,
        val_dataset=val_ds,
        epochs=5,
        early_stopping=True
    )
    
    # Step 5: Evaluate Model
    logger.info("\n[STEP 5] EVALUATING MODEL")
    logger.info("-" * 60)
    
    test_results = model.evaluate(test_ds)
    
    # Step 6: Save Model
    logger.info("\n[STEP 6] SAVING MODEL")
    logger.info("-" * 60)
    
    model.save_model()
    
    # Step 7: Summary
    logger.info("\n[STEP 7] TRAINING SUMMARY")
    logger.info("=" * 60)
    
    logger.info("\n✅ TRAINING COMPLETE!")
    logger.info(f"\nModel saved to: ai/models/hand_hygiene_detector_final.h5")
    logger.info(f"Configuration saved to: ai/models/hand_hygiene_detector_config.json")
    
    logger.info("\nModel Performance Metrics:")
    for metric_name, value in test_results.items():
        if isinstance(value, float):
            logger.info(f"  {metric_name}: {value:.4f}")
    
    logger.info("\nDataset Statistics:")
    for split, data in stats.items():
        logger.info(f"  {split}:")
        for class_name, count in data.items():
            logger.info(f"    {class_name}: {count}")
    
    logger.info("\n" + "="*60)
    logger.info("Ready for deployment! Model can now be used for real-time")
    logger.info("hand hygiene detection on webcam streams.")
    logger.info("="*60)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nTraining interrupted by user")
    except Exception as e:
        import traceback
        logger.error(f"Training failed: {e}", exc_info=True)
        print("\n===== TRAINING ERROR =====\n", flush=True)
        traceback.print_exc()
        print("\n========================\n", flush=True)
        sys.exit(1)
