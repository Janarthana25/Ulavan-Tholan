"""
Ulavan Tholan - Plant Disease Detection Model Training
Dataset: PlantVillage - https://www.kaggle.com/datasets/mohitsingh1804/plantvillage
Model: MobileNetV2 with Transfer Learning
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix
import json
import os

# Configuration
IMG_SIZE = 224
BATCH_SIZE = 32
EPOCHS = 50
DATASET_PATH = 'plantvillage'  # Path to extracted PlantVillage dataset
MODEL_SAVE_PATH = 'models/plant_disease_model.h5'
CLASSES_SAVE_PATH = 'models/class_names.json'

class PlantDiseaseModel:
    def __init__(self, dataset_path, img_size=224):
        self.dataset_path = dataset_path
        self.img_size = img_size
        self.model = None
        self.class_names = []
        self.history = None
        
    def prepare_data(self):
        """Prepare training and validation data with augmentation"""
        print("📊 Preparing dataset...")
        
        # Training data augmentation
        train_datagen = ImageDataGenerator(
            rescale=1./255,
            rotation_range=30,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True,
            vertical_flip=True,
            fill_mode='nearest',
            validation_split=0.2
        )
        
        # Validation data (only rescaling)
        val_datagen = ImageDataGenerator(
            rescale=1./255,
            validation_split=0.2
        )
        
        # Training generator
        self.train_generator = train_datagen.flow_from_directory(
            self.dataset_path,
            target_size=(self.img_size, self.img_size),
            batch_size=BATCH_SIZE,
            class_mode='categorical',
            subset='training'
        )
        
        # Validation generator
        self.val_generator = val_datagen.flow_from_directory(
            self.dataset_path,
            target_size=(self.img_size, self.img_size),
            batch_size=BATCH_SIZE,
            class_mode='categorical',
            subset='validation'
        )
        
        # Store class names
        self.class_names = list(self.train_generator.class_indices.keys())
        print(f"✅ Found {len(self.class_names)} disease classes")
        
        return self.train_generator, self.val_generator
    
    def build_model(self):
        """Build MobileNetV2 based model with transfer learning"""
        print("🏗️ Building MobileNetV2 model...")
        
        # Load pre-trained MobileNetV2
        base_model = MobileNetV2(
            input_shape=(self.img_size, self.img_size, 3),
            include_top=False,
            weights='imagenet'
        )
        
        # Freeze base model layers
        base_model.trainable = False
        
        # Build custom top layers
        inputs = keras.Input(shape=(self.img_size, self.img_size, 3))
        x = base_model(inputs, training=False)
        x = layers.GlobalAveragePooling2D()(x)
        x = layers.Dense(512, activation='relu')(x)
        x = layers.Dropout(0.5)(x)
        x = layers.Dense(256, activation='relu')(x)
        x = layers.Dropout(0.3)(x)
        outputs = layers.Dense(len(self.class_names), activation='softmax')(x)
        
        self.model = keras.Model(inputs, outputs)
        
        # Compile model
        self.model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy', keras.metrics.Precision(), keras.metrics.Recall()]
        )
        
        print("✅ Model built successfully")
        print(self.model.summary())
        
        return self.model
    
    def train(self):
        """Train the model with callbacks"""
        print("🚀 Starting training...")
        
        # Create models directory
        os.makedirs('models', exist_ok=True)
        
        # Callbacks
        callbacks = [
            EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True,
                verbose=1
            ),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-7,
                verbose=1
            ),
            ModelCheckpoint(
                MODEL_SAVE_PATH,
                monitor='val_accuracy',
                save_best_only=True,
                verbose=1
            )
        ]
        
        # Train model
        self.history = self.model.fit(
            self.train_generator,
            validation_data=self.val_generator,
            epochs=EPOCHS,
            callbacks=callbacks
        )
        
        print("✅ Training completed!")
        return self.history
    
    def fine_tune(self):
        """Fine-tune the model by unfreezing base layers"""
        print("🔧 Fine-tuning model...")
        
        # Unfreeze base model
        base_model = self.model.layers[1]
        base_model.trainable = True
        
        # Freeze early layers, fine-tune later layers
        for layer in base_model.layers[:100]:
            layer.trainable = False
        
        # Recompile with lower learning rate
        self.model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=1e-5),
            loss='categorical_crossentropy',
            metrics=['accuracy', keras.metrics.Precision(), keras.metrics.Recall()]
        )
        
        # Train for additional epochs
        callbacks = [
            EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True),
            ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, min_lr=1e-8)
        ]
        
        fine_tune_history = self.model.fit(
            self.train_generator,
            validation_data=self.val_generator,
            epochs=20,
            callbacks=callbacks
        )
        
        # Save final model
        self.model.save(MODEL_SAVE_PATH)
        print(f"✅ Model saved to {MODEL_SAVE_PATH}")
        
    def save_class_names(self):
        """Save class names to JSON"""
        with open(CLASSES_SAVE_PATH, 'w') as f:
            json.dump(self.class_names, f, indent=2)
        print(f"✅ Class names saved to {CLASSES_SAVE_PATH}")
    
    def evaluate(self):
        """Evaluate model and generate metrics"""
        print("📊 Evaluating model...")
        
        # Get predictions
        predictions = self.model.predict(self.val_generator)
        y_pred = np.argmax(predictions, axis=1)
        y_true = self.val_generator.classes
        
        # Classification report
        print("\n📈 Classification Report:")
        print(classification_report(y_true, y_pred, target_names=self.class_names))
        
        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        
        # Plot confusion matrix
        plt.figure(figsize=(20, 20))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Greens', 
                    xticklabels=self.class_names, yticklabels=self.class_names)
        plt.title('Confusion Matrix - Plant Disease Detection')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        plt.savefig('models/confusion_matrix.png')
        print("✅ Confusion matrix saved")
        
    def plot_training_history(self):
        """Plot training metrics"""
        if self.history is None:
            print("❌ No training history available")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Accuracy
        axes[0, 0].plot(self.history.history['accuracy'], label='Train')
        axes[0, 0].plot(self.history.history['val_accuracy'], label='Validation')
        axes[0, 0].set_title('Model Accuracy')
        axes[0, 0].set_xlabel('Epoch')
        axes[0, 0].set_ylabel('Accuracy')
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        
        # Loss
        axes[0, 1].plot(self.history.history['loss'], label='Train')
        axes[0, 1].plot(self.history.history['val_loss'], label='Validation')
        axes[0, 1].set_title('Model Loss')
        axes[0, 1].set_xlabel('Epoch')
        axes[0, 1].set_ylabel('Loss')
        axes[0, 1].legend()
        axes[0, 1].grid(True)
        
        # Precision
        axes[1, 0].plot(self.history.history['precision'], label='Train')
        axes[1, 0].plot(self.history.history['val_precision'], label='Validation')
        axes[1, 0].set_title('Model Precision')
        axes[1, 0].set_xlabel('Epoch')
        axes[1, 0].set_ylabel('Precision')
        axes[1, 0].legend()
        axes[1, 0].grid(True)
        
        # Recall
        axes[1, 1].plot(self.history.history['recall'], label='Train')
        axes[1, 1].plot(self.history.history['val_recall'], label='Validation')
        axes[1, 1].set_title('Model Recall')
        axes[1, 1].set_xlabel('Epoch')
        axes[1, 1].set_ylabel('Recall')
        axes[1, 1].legend()
        axes[1, 1].grid(True)
        
        plt.tight_layout()
        plt.savefig('models/training_history.png')
        print("✅ Training history plots saved")

def main():
    """Main training pipeline"""
    print("🌱 Ulavan Tholan - Plant Disease Detection Training")
    print("=" * 60)
    
    # Initialize model
    model_trainer = PlantDiseaseModel(DATASET_PATH, IMG_SIZE)
    
    # Prepare data
    model_trainer.prepare_data()
    
    # Build model
    model_trainer.build_model()
    
    # Train model
    model_trainer.train()
    
    # Fine-tune model
    model_trainer.fine_tune()
    
    # Save class names
    model_trainer.save_class_names()
    
    # Evaluate model
    model_trainer.evaluate()
    
    # Plot training history
    model_trainer.plot_training_history()
    
    print("\n✅ Training pipeline completed successfully!")
    print(f"📦 Model saved at: {MODEL_SAVE_PATH}")
    print(f"📋 Class names saved at: {CLASSES_SAVE_PATH}")

if __name__ == "__main__":
    main()
