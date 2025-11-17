"""
Real-time Face Emotion Detection System
Uses device camera to detect and analyze facial emotions
Based on Kaggle Human Face Emotions Dataset
"""

import cv2
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dense, Dropout, Flatten, BatchNormalization
from tensorflow.keras.preprocessing.image import img_to_array
import os

class EmotionDetector:
    """Class to handle emotion detection from facial images"""
    
    def __init__(self, model_path=None):
        """Initialize the emotion detector"""
        self.emotions = ['Angry', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise']
        self.model = None
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Load or create model
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        else:
            self.model = self.create_model()
            print("Warning: Using untrained model. For best results, train the model first.")
    
    def create_model(self):
        """
        Create CNN model for emotion detection
        Architecture based on common FER (Facial Expression Recognition) models
        """
        model = Sequential()
        
        # First Convolutional Block
        model.add(Conv2D(32, (3, 3), activation='relu', input_shape=(48, 48, 1)))
        model.add(BatchNormalization())
        model.add(Conv2D(64, (3, 3), activation='relu'))
        model.add(BatchNormalization())
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Dropout(0.25))
        
        # Second Convolutional Block
        model.add(Conv2D(128, (3, 3), activation='relu'))
        model.add(BatchNormalization())
        model.add(Conv2D(128, (3, 3), activation='relu'))
        model.add(BatchNormalization())
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Dropout(0.25))
        
        # Third Convolutional Block
        model.add(Conv2D(256, (3, 3), activation='relu'))
        model.add(BatchNormalization())
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Dropout(0.25))
        
        # Fully Connected Layers
        model.add(Flatten())
        model.add(Dense(512, activation='relu'))
        model.add(BatchNormalization())
        model.add(Dropout(0.5))
        model.add(Dense(256, activation='relu'))
        model.add(BatchNormalization())
        model.add(Dropout(0.5))
        model.add(Dense(7, activation='softmax'))
        
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        
        return model
    
    def load_model(self, model_path):
        """Load a pre-trained model"""
        from tensorflow.keras.models import load_model
        self.model = load_model(model_path)
        print(f"Model loaded from {model_path}")
    
    def save_model(self, model_path):
        """Save the trained model"""
        if self.model:
            self.model.save(model_path)
            print(f"Model saved to {model_path}")
    
    def detect_faces(self, frame):
        """Detect faces in the given frame"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        return faces, gray
    
    def predict_emotion(self, face_img):
        """Predict emotion from a face image"""
        if self.model is None:
            return None, []
        
        # Preprocess the face image
        face_img = cv2.resize(face_img, (48, 48))
        face_img = face_img.astype('float32') / 255.0
        face_img = img_to_array(face_img)
        face_img = np.expand_dims(face_img, axis=0)
        
        # Predict emotion
        predictions = self.model.predict(face_img, verbose=0)
        emotion_idx = np.argmax(predictions[0])
        emotion = self.emotions[emotion_idx]
        confidence = predictions[0][emotion_idx]
        
        return emotion, predictions[0]
    
    def draw_emotion_info(self, frame, x, y, w, h, emotion, confidence, all_predictions):
        """Draw emotion information on the frame"""
        # Draw rectangle around face
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        # Draw emotion label
        label = f"{emotion}: {confidence*100:.1f}%"
        cv2.putText(frame, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        
        # Draw emotion probabilities bar chart on the side
        bar_height = 20
        bar_width = 200
        start_x = frame.shape[1] - bar_width - 20
        start_y = 50
        
        for i, (emotion_name, prob) in enumerate(zip(self.emotions, all_predictions)):
            # Background bar
            cv2.rectangle(frame, (start_x, start_y + i * (bar_height + 5)), 
                         (start_x + bar_width, start_y + i * (bar_height + 5) + bar_height), 
                         (50, 50, 50), -1)
            
            # Probability bar
            bar_fill = int(bar_width * prob)
            color = (0, 255, 0) if emotion_name == emotion else (100, 100, 255)
            cv2.rectangle(frame, (start_x, start_y + i * (bar_height + 5)), 
                         (start_x + bar_fill, start_y + i * (bar_height + 5) + bar_height), 
                         color, -1)
            
            # Emotion name and percentage
            text = f"{emotion_name}: {prob*100:.1f}%"
            cv2.putText(frame, text, (start_x + 5, start_y + i * (bar_height + 5) + 15), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return frame
    
    def run_realtime_detection(self):
        """Run real-time emotion detection from camera"""
        print("Starting camera... Press 'q' to quit")
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error: Could not open camera")
            return
        
        # Set camera properties for better performance
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        print("Camera started successfully!")
        print("Controls:")
        print("  'q' - Quit")
        print("  's' - Save screenshot")
        
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame")
                break
            
            frame_count += 1
            
            # Detect faces
            faces, gray = self.detect_faces(frame)
            
            # Process each face
            for (x, y, w, h) in faces:
                face_roi = gray[y:y+h, x:x+w]
                
                # Predict emotion
                emotion, predictions = self.predict_emotion(face_roi)
                
                if emotion:
                    confidence = np.max(predictions)
                    # Draw emotion information
                    frame = self.draw_emotion_info(frame, x, y, w, h, emotion, confidence, predictions)
            
            # Add title and instructions
            cv2.putText(frame, "Face Emotion Detection - Real-time", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(frame, f"Faces detected: {len(faces)}", (10, frame.shape[0] - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            # Display the frame
            cv2.imshow('Face Emotion Detection', frame)
            
            # Check for key press
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("Quitting...")
                break
            elif key == ord('s'):
                screenshot_path = f"emotion_screenshot_{frame_count}.png"
                cv2.imwrite(screenshot_path, frame)
                print(f"Screenshot saved: {screenshot_path}")
        
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        print("Camera stopped")


def main():
    """Main function to run the emotion detector"""
    print("=" * 60)
    print("Real-time Face Emotion Detection System")
    print("Based on Kaggle Human Face Emotions Dataset")
    print("=" * 60)
    print()
    
    # Initialize detector
    detector = EmotionDetector()
    
    # Run real-time detection
    detector.run_realtime_detection()


if __name__ == "__main__":
    main()
