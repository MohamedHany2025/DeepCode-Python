# ML Image Classifier - Deep Learning Model for Image Classification
# Project: ML Image Classifier
# Language: Python
# Description: Deep learning model for image classification with custom training pipeline and inference optimization

import numpy as np
from tensorflow import keras
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications import EfficientNetB0
import matplotlib.pyplot as plt
from typing import Tuple, List, Dict, Optional
import os
from datetime import datetime
import json

# ==================== Configuration ====================
class ClassifierConfig:
    def __init__(self):
        self.img_height = 224
        self.img_width = 224
        self.batch_size = 32
        self.epochs = 50
        self.learning_rate = 0.001
        self.validation_split = 0.2
        self.test_split = 0.1
        self.num_classes = 10
        self.model_name = "image_classifier"
        self.save_dir = "./models"

# ==================== Custom Layers & Callbacks ====================
class FocusedDropout(layers.Layer):
    """Custom dropout layer with focused regularization"""
    def __init__(self, rate=0.5, **kwargs):
        super().__init__(**kwargs)
        self.rate = rate
    
    def call(self, inputs, training=None):
        if training:
            mask = np.random.binomial(1, 1-self.rate, inputs.shape)
            return inputs * mask / (1 - self.rate)
        return inputs

class PerformanceCallback(keras.callbacks.Callback):
    """Custom callback for training monitoring"""
    def __init__(self, val_data=None):
        super().__init__()
        self.val_data = val_data
        self.history = {
            'accuracy': [],
            'loss': [],
            'val_accuracy': [],
            'val_loss': []
        }
    
    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        self.history['accuracy'].append(logs.get('accuracy', 0))
        self.history['loss'].append(logs.get('loss', 0))
        self.history['val_accuracy'].append(logs.get('val_accuracy', 0))
        self.history['val_loss'].append(logs.get('val_loss', 0))
        
        if (epoch + 1) % 10 == 0:
            print(f"\nEpoch {epoch + 1}: "
                  f"Train Acc={logs.get('accuracy', 0):.4f}, "
                  f"Val Acc={logs.get('val_accuracy', 0):.4f}")

# ==================== Model Builder ====================
class ImageClassifier:
    def __init__(self, config: Optional[ClassifierConfig] = None):
        self.config = config or ClassifierConfig()
        self.model = None
        self.history = None
        self.class_names = []
        self.performance_metrics = {}
    
    def build_model(self, use_pretrained: bool = True) -> keras.Model:
        """Build CNN model with transfer learning"""
        if use_pretrained:
            # Use EfficientNetB0 as backbone
            base_model = EfficientNetB0(
                input_shape=(self.config.img_height, self.config.img_width, 3),
                weights='imagenet',
                include_top=False
            )
            
            # Freeze base model layers
            base_model.trainable = False
            
            model = models.Sequential([
                base_model,
                layers.GlobalAveragePooling2D(),
                layers.Dense(256, activation='relu'),
                FocusedDropout(0.3),
                layers.Dense(128, activation='relu'),
                layers.BatchNormalization(),
                FocusedDropout(0.2),
                layers.Dense(self.config.num_classes, activation='softmax')
            ])
        else:
            # Custom CNN architecture
            model = models.Sequential([
                layers.Conv2D(32, 3, activation='relu', 
                            input_shape=(self.config.img_height, self.config.img_width, 3)),
                layers.MaxPooling2D(2),
                layers.Conv2D(64, 3, activation='relu'),
                layers.MaxPooling2D(2),
                layers.Conv2D(128, 3, activation='relu'),
                layers.MaxPooling2D(2),
                layers.Conv2D(256, 3, activation='relu'),
                layers.GlobalAveragePooling2D(),
                layers.Dense(256, activation='relu'),
                FocusedDropout(0.5),
                layers.Dense(128, activation='relu'),
                layers.Dense(self.config.num_classes, activation='softmax')
            ])
        
        self.model = model
        return model
    
    def compile_model(self, optimizer: Optional[str] = None, loss: Optional[str] = None):
        """Compile the model"""
        if self.model is None:
            raise ValueError("Model not built. Call build_model first.")
        
        optimizer = optimizer or keras.optimizers.Adam(
            learning_rate=self.config.learning_rate
        )
        loss = loss or 'categorical_crossentropy'
        
        self.model.compile(
            optimizer=optimizer,
            loss=loss,
            metrics=['accuracy', keras.metrics.Precision(), keras.metrics.Recall()]
        )
    
    def prepare_data(self, data_path: str) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Prepare and load data"""
        # This is a template - adjust based on your data structure
        images = []
        labels = []
        self.class_names = []
        
        for class_idx, class_name in enumerate(os.listdir(data_path)):
            class_path = os.path.join(data_path, class_name)
            if not os.path.isdir(class_path):
                continue
            
            self.class_names.append(class_name)
            
            for img_file in os.listdir(class_path):
                img_path = os.path.join(class_path, img_file)
                try:
                    img = image.load_img(img_path, 
                                        target_size=(self.config.img_height, 
                                                   self.config.img_width))
                    img_array = image.img_to_array(img) / 255.0
                    images.append(img_array)
                    labels.append(class_idx)
                except Exception as e:
                    print(f"Error loading {img_path}: {e}")
        
        return np.array(images), keras.utils.to_categorical(labels), self.class_names
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray,
              X_val: Optional[np.ndarray] = None, y_val: Optional[np.ndarray] = None):
        """Train the model"""
        if self.model is None:
            raise ValueError("Model not built. Call build_model and compile_model first.")
        
        callbacks = [
            PerformanceCallback(),
            keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=5,
                restore_best_weights=True
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=3,
                min_lr=1e-7
            )
        ]
        
        self.history = self.model.fit(
            X_train, y_train,
            batch_size=self.config.batch_size,
            epochs=self.config.epochs,
            validation_data=(X_val, y_val) if X_val is not None else self.config.validation_split,
            callbacks=callbacks,
            verbose=1
        )
    
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict:
        """Evaluate model on test set"""
        results = self.model.evaluate(X_test, y_test, verbose=0)
        
        self.performance_metrics = {
            'test_loss': float(results[0]),
            'test_accuracy': float(results[1]),
            'test_precision': float(results[2]),
            'test_recall': float(results[3]),
            'timestamp': datetime.now().isoformat()
        }
        
        return self.performance_metrics
    
    def predict(self, img_path: str) -> Tuple[str, float]:
        """Predict class for single image"""
        img = image.load_img(img_path, 
                            target_size=(self.config.img_height, self.config.img_width))
        img_array = image.img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        
        predictions = self.model.predict(img_array, verbose=0)
        predicted_class_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_class_idx])
        
        return self.class_names[predicted_class_idx], confidence
    
    def predict_batch(self, img_paths: List[str]) -> List[Tuple[str, float]]:
        """Predict classes for multiple images"""
        results = []
        for img_path in img_paths:
            class_name, confidence = self.predict(img_path)
            results.append((class_name, confidence))
        return results
    
    def save_model(self, save_path: Optional[str] = None):
        """Save model to disk"""
        if self.model is None:
            raise ValueError("No model to save")
        
        save_path = save_path or os.path.join(
            self.config.save_dir,
            f"{self.config.model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        os.makedirs(self.config.save_dir, exist_ok=True)
        
        self.model.save(save_path)
        
        # Save metadata
        metadata = {
            'class_names': self.class_names,
            'config': {
                'img_height': self.config.img_height,
                'img_width': self.config.img_width,
                'num_classes': self.config.num_classes
            },
            'performance': self.performance_metrics,
            'saved_at': datetime.now().isoformat()
        }
        
        with open(f"{save_path}_metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"Model saved to {save_path}")
    
    def load_model(self, model_path: str):
        """Load model from disk"""
        self.model = keras.models.load_model(model_path)
        print(f"Model loaded from {model_path}")
    
    def plot_training_history(self):
        """Plot training history"""
        if self.history is None:
            print("No training history available")
            return
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 4))
        
        axes[0].plot(self.history.history['accuracy'], label='Train Accuracy')
        axes[0].plot(self.history.history['val_accuracy'], label='Val Accuracy')
        axes[0].set_title('Model Accuracy')
        axes[0].set_xlabel('Epoch')
        axes[0].set_ylabel('Accuracy')
        axes[0].legend()
        
        axes[1].plot(self.history.history['loss'], label='Train Loss')
        axes[1].plot(self.history.history['val_loss'], label='Val Loss')
        axes[1].set_title('Model Loss')
        axes[1].set_xlabel('Epoch')
        axes[1].set_ylabel('Loss')
        axes[1].legend()
        
        plt.tight_layout()
        plt.show()

# ==================== Usage Example ====================
if __name__ == "__main__":
    # Initialize classifier
    config = ClassifierConfig()
    config.epochs = 30
    config.batch_size = 32
    
    classifier = ImageClassifier(config)
    
    # Build and compile model
    classifier.build_model(use_pretrained=True)
    classifier.compile_model()
    
    print("Model Summary:")
    classifier.model.summary()
    
    # In practice, you would load actual data:
    # X_train, y_train, class_names = classifier.prepare_data("path/to/train/data")
    # X_val, y_val, _ = classifier.prepare_data("path/to/val/data")
    # classifier.train(X_train, y_train, X_val, y_val)
    # metrics = classifier.evaluate(X_test, y_test)
    # classifier.save_model()
    
    print("Image Classifier ready for training!")
