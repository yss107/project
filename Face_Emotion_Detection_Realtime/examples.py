"""
Example usage scenarios for Face Emotion Detection system
Demonstrates different ways to use the emotion detector
"""

from emotion_detector import EmotionDetector
import cv2
import numpy as np


def example_1_basic_detection():
    """Example 1: Basic real-time detection"""
    print("\n" + "="*60)
    print("Example 1: Basic Real-time Detection")
    print("="*60)
    print("This will start the camera and detect emotions in real-time")
    print("Press 'q' to quit\n")
    
    input("Press Enter to start...")
    
    detector = EmotionDetector()
    detector.run_realtime_detection()


def example_2_single_frame():
    """Example 2: Process a single frame"""
    print("\n" + "="*60)
    print("Example 2: Single Frame Processing")
    print("="*60)
    print("Capture and analyze a single frame\n")
    
    input("Press Enter to capture...")
    
    detector = EmotionDetector()
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Cannot open camera")
        return
    
    # Capture frame
    ret, frame = cap.read()
    if ret:
        faces, gray = detector.detect_faces(frame)
        
        if len(faces) == 0:
            print("No faces detected in frame")
        else:
            print(f"Found {len(faces)} face(s)")
            
            for i, (x, y, w, h) in enumerate(faces):
                face_roi = gray[y:y+h, x:x+w]
                emotion, predictions = detector.predict_emotion(face_roi)
                
                if emotion:
                    print(f"\nFace {i+1}:")
                    print(f"  Emotion: {emotion}")
                    print(f"  Confidence: {np.max(predictions)*100:.1f}%")
                    print("  All probabilities:")
                    for emo, prob in zip(detector.emotions, predictions):
                        print(f"    {emo}: {prob*100:.1f}%")
    
    cap.release()
    print("\nFrame processed!")


def example_3_emotion_tracking():
    """Example 3: Track dominant emotion over time"""
    print("\n" + "="*60)
    print("Example 3: Emotion Tracking Over Time")
    print("="*60)
    print("Track your dominant emotion for 10 seconds")
    print("Press 'q' to quit early\n")
    
    input("Press Enter to start...")
    
    detector = EmotionDetector()
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Cannot open camera")
        return
    
    emotion_counts = {emo: 0 for emo in detector.emotions}
    frame_count = 0
    max_frames = 300  # ~10 seconds at 30fps
    
    print("\nTracking emotions...")
    
    while frame_count < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        
        faces, gray = detector.detect_faces(frame)
        
        for (x, y, w, h) in faces:
            face_roi = gray[y:y+h, x:x+w]
            emotion, predictions = detector.predict_emotion(face_roi)
            
            if emotion:
                emotion_counts[emotion] += 1
        
        frame_count += 1
        
        # Display progress
        if frame_count % 30 == 0:
            print(f"  {frame_count//30} seconds...")
        
        # Check for quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    # Results
    print("\n" + "="*60)
    print("Emotion Tracking Results")
    print("="*60)
    
    total = sum(emotion_counts.values())
    if total == 0:
        print("No emotions detected")
        return
    
    print(f"\nTotal detections: {total}")
    print("\nEmotion Distribution:")
    
    # Sort by count
    sorted_emotions = sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)
    
    for emotion, count in sorted_emotions:
        percentage = (count / total) * 100
        bar = "█" * int(percentage / 2)
        print(f"  {emotion:10s}: {bar} {percentage:5.1f}% ({count})")
    
    dominant = sorted_emotions[0][0]
    print(f"\nDominant emotion: {dominant}")


def example_4_custom_processing():
    """Example 4: Custom processing with emotion data"""
    print("\n" + "="*60)
    print("Example 4: Custom Processing")
    print("="*60)
    print("Detect emotions and trigger actions based on results\n")
    
    input("Press Enter to start...")
    
    detector = EmotionDetector()
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Cannot open camera")
        return
    
    print("\nWatching for happy emotions...")
    print("Smile to trigger action! (Press 'q' to quit)")
    
    happy_threshold = 0.7  # 70% confidence
    happy_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        faces, gray = detector.detect_faces(frame)
        
        for (x, y, w, h) in faces:
            face_roi = gray[y:y+h, x:x+w]
            emotion, predictions = detector.predict_emotion(face_roi)
            
            if emotion == 'Happy' and predictions[3] > happy_threshold:  # Happy is index 3
                happy_count += 1
                print(f"😊 Happy detected! (Count: {happy_count})")
                
                # Custom action: You could trigger anything here
                # - Play a sound
                # - Save a photo
                # - Send a notification
                # - Update a database
                # etc.
        
        # Display frame
        cv2.imshow('Custom Processing - Smile to trigger', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    print(f"\nTotal happy moments detected: {happy_count}")


def main():
    """Main menu for examples"""
    print("="*60)
    print("Face Emotion Detection - Usage Examples")
    print("="*60)
    
    examples = [
        ("Basic Real-time Detection", example_1_basic_detection),
        ("Single Frame Analysis", example_2_single_frame),
        ("Emotion Tracking Over Time", example_3_emotion_tracking),
        ("Custom Processing", example_4_custom_processing)
    ]
    
    while True:
        print("\nAvailable Examples:")
        for i, (name, _) in enumerate(examples, 1):
            print(f"{i}. {name}")
        print("0. Exit")
        
        choice = input("\nSelect an example (0-4): ")
        
        if choice == '0':
            print("Goodbye!")
            break
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(examples):
                examples[idx][1]()
            else:
                print("Invalid choice!")
        except (ValueError, IndexError):
            print("Invalid input!")


if __name__ == "__main__":
    main()
