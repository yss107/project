"""
Training script for Face Emotion Detection Model
Compatible with Kaggle Human Face Emotions Dataset
https://www.kaggle.com/datasets/samithsachidanandan/human-face-emotions
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from emotion_detector import EmotionDetector


class EmotionModelTrainer:
    """Class to handle training of emotion detection model"""
    
    def __init__(self):
        """Initialize the trainer"""
        self.detector = EmotionDetector()
        self.model = self.detector.model
        self.emotions = self.detector.emotions
        self.history = None
    
    def load_kaggle_dataset(self, csv_path):
        """
        Load the Kaggle Human Face Emotions dataset
        Expected format: CSV with 'emotion' and 'pixels' columns
        emotion: 0=Angry, 1=Disgust, 2=Fear, 3=Happy, 4=Sad, 5=Surprise, 6=Neutral
        pixels: space-separated pixel values (48x48 grayscale image)
        """
        print("Loading dataset...")
        df = pd.read_csv(csv_path)
        
        # Extract emotions and pixels
        emotions = df['emotion'].values
        pixels = df['pixels'].values
        
        # Convert pixels to numpy arrays
        X = []
        for pixel_sequence in pixels:
            pixel_list = [int(pixel) for pixel in pixel_sequence.split(' ')]
            image = np.array(pixel_list).reshape(48, 48, 1)
            X.append(image)
        
        X = np.array(X, dtype='float32')
        y = to_categorical(emotions, num_classes=7)
        
        print(f"Dataset loaded: {X.shape[0]} images")
        print(f"Image shape: {X.shape[1:]}")
        print(f"Emotion distribution:")
        for i, emotion in enumerate(self.emotions):
            count = np.sum(emotions == i)
            print(f"  {emotion}: {count} ({count/len(emotions)*100:.1f}%)")
        
        return X, y
    
    def load_from_directory(self, data_dir):
        """
        Load dataset from directory structure
        Expected structure: data_dir/emotion_name/image.jpg
        """
        print("Loading dataset from directory...")
        X = []
        y = []
        
        for emotion_idx, emotion_name in enumerate(self.emotions):
            emotion_dir = os.path.join(data_dir, emotion_name.lower())
            if not os.path.exists(emotion_dir):
                print(f"Warning: Directory not found: {emotion_dir}")
                continue
            
            image_files = [f for f in os.listdir(emotion_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
            print(f"Loading {emotion_name}: {len(image_files)} images")
            
            for img_file in image_files:
                img_path = os.path.join(emotion_dir, img_file)
                try:
                    import cv2
                    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                    if img is not None:
                        img = cv2.resize(img, (48, 48))
                        img = img.reshape(48, 48, 1)
                        X.append(img)
                        y.append(emotion_idx)
                except Exception as e:
                    print(f"Error loading {img_path}: {e}")
        
        X = np.array(X, dtype='float32')
        y = to_categorical(y, num_classes=7)
        
        print(f"Dataset loaded: {X.shape[0]} images")
        return X, y
    
    def preprocess_data(self, X, y, validation_split=0.2):
        """Preprocess and split the data"""
        print("\nPreprocessing data...")
        
        # Normalize pixel values
        X = X / 255.0
        
        # Split into train and validation sets
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=validation_split, random_state=42, stratify=np.argmax(y, axis=1)
        )
        
        print(f"Training samples: {X_train.shape[0]}")
        print(f"Validation samples: {X_val.shape[0]}")
        
        return X_train, X_val, y_train, y_val
    
    def train(self, X_train, y_train, X_val, y_val, epochs=50, batch_size=64, use_augmentation=True):
        """Train the model"""
        print("\nStarting training...")
        print(f"Epochs: {epochs}, Batch size: {batch_size}")
        print(f"Data augmentation: {use_augmentation}")
        
        # Callbacks
        checkpoint = ModelCheckpoint(
            'emotion_model_best.h5',
            monitor='val_accuracy',
            save_best_only=True,
            mode='max',
            verbose=1
        )
        
        early_stopping = EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True,
            verbose=1
        )
        
        reduce_lr = ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-7,
            verbose=1
        )
        
        callbacks = [checkpoint, early_stopping, reduce_lr]
        
        # Data augmentation
        if use_augmentation:
            datagen = ImageDataGenerator(
                rotation_range=15,
                width_shift_range=0.1,
                height_shift_range=0.1,
                horizontal_flip=True,
                zoom_range=0.1,
                fill_mode='nearest'
            )
            datagen.fit(X_train)
            
            self.history = self.model.fit(
                datagen.flow(X_train, y_train, batch_size=batch_size),
                validation_data=(X_val, y_val),
                epochs=epochs,
                callbacks=callbacks,
                verbose=1
            )
        else:
            self.history = self.model.fit(
                X_train, y_train,
                validation_data=(X_val, y_val),
                epochs=epochs,
                batch_size=batch_size,
                callbacks=callbacks,
                verbose=1
            )
        
        print("\nTraining completed!")
        return self.history
    
    def plot_training_history(self, save_path='training_history.png'):
        """Plot training history"""
        if self.history is None:
            print("No training history available")
            return
        
        fig, axes = plt.subplots(1, 2, figsize=(15, 5))
        
        # Accuracy plot
        axes[0].plot(self.history.history['accuracy'], label='Training Accuracy')
        axes[0].plot(self.history.history['val_accuracy'], label='Validation Accuracy')
        axes[0].set_title('Model Accuracy')
        axes[0].set_xlabel('Epoch')
        axes[0].set_ylabel('Accuracy')
        axes[0].legend()
        axes[0].grid(True)
        
        # Loss plot
        axes[1].plot(self.history.history['loss'], label='Training Loss')
        axes[1].plot(self.history.history['val_loss'], label='Validation Loss')
        axes[1].set_title('Model Loss')
        axes[1].set_xlabel('Epoch')
        axes[1].set_ylabel('Loss')
        axes[1].legend()
        axes[1].grid(True)
        
        plt.tight_layout()
        plt.savefig(save_path)
        print(f"Training history plot saved: {save_path}")
        plt.close()
    
    def evaluate(self, X_test, y_test):
        """Evaluate the model"""
        print("\nEvaluating model...")
        loss, accuracy = self.model.evaluate(X_test, y_test, verbose=0)
        print(f"Test Loss: {loss:.4f}")
        print(f"Test Accuracy: {accuracy:.4f}")
        
        # Detailed classification report
        from sklearn.metrics import classification_report, confusion_matrix
        import seaborn as sns
        
        y_pred = self.model.predict(X_test, verbose=0)
        y_pred_classes = np.argmax(y_pred, axis=1)
        y_true_classes = np.argmax(y_test, axis=1)
        
        print("\nClassification Report:")
        print(classification_report(y_true_classes, y_pred_classes, target_names=self.emotions))
        
        # Confusion matrix
        cm = confusion_matrix(y_true_classes, y_pred_classes)
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                   xticklabels=self.emotions, yticklabels=self.emotions)
        plt.title('Confusion Matrix')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        plt.savefig('confusion_matrix.png')
        print("Confusion matrix saved: confusion_matrix.png")
        plt.close()
        
        return accuracy
    
    def save_model(self, path='emotion_model_final.h5'):
        """Save the trained model"""
        self.model.save(path)
        print(f"Model saved: {path}")


def main():
    """Main training function"""
    print("=" * 60)
    print("Face Emotion Detection - Model Training")
    print("=" * 60)
    print()
    
    # Initialize trainer
    trainer = EmotionModelTrainer()
    
    # Option 1: Load from Kaggle CSV format
    print("Dataset loading options:")
    print("1. Load from CSV file (Kaggle format)")
    print("2. Load from directory structure")
    choice = input("Enter choice (1 or 2): ")
    
    if choice == '1':
        csv_path = input("Enter path to CSV file: ")
        if not os.path.exists(csv_path):
            print(f"Error: File not found: {csv_path}")
            return
        X, y = trainer.load_kaggle_dataset(csv_path)
    elif choice == '2':
        data_dir = input("Enter path to data directory: ")
        if not os.path.exists(data_dir):
            print(f"Error: Directory not found: {data_dir}")
            return
        X, y = trainer.load_from_directory(data_dir)
    else:
        print("Invalid choice")
        return
    
    # Preprocess data
    X_train, X_val, y_train, y_val = trainer.preprocess_data(X, y)
    
    # Training parameters
    epochs = int(input("Enter number of epochs (default 50): ") or "50")
    batch_size = int(input("Enter batch size (default 64): ") or "64")
    use_augmentation = input("Use data augmentation? (y/n, default y): ").lower() != 'n'
    
    # Train model
    trainer.train(X_train, y_train, X_val, y_val, epochs=epochs, 
                 batch_size=batch_size, use_augmentation=use_augmentation)
    
    # Plot training history
    trainer.plot_training_history()
    
    # Evaluate on validation set
    trainer.evaluate(X_val, y_val)
    
    # Save model
    trainer.save_model()
    
    print("\nTraining complete!")
    print("Model files saved:")
    print("  - emotion_model_best.h5 (best validation accuracy)")
    print("  - emotion_model_final.h5 (final model)")
    print("  - training_history.png")
    print("  - confusion_matrix.png")


if __name__ == "__main__":
    main()
