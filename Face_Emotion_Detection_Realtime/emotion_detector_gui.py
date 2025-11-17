"""
GUI Interface for Face Emotion Detection
Provides a user-friendly interface with emotion analysis
"""

import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk
import threading
import numpy as np
from emotion_detector import EmotionDetector


class EmotionDetectorGUI:
    """GUI Application for Real-time Emotion Detection"""
    
    def __init__(self, root):
        """Initialize the GUI"""
        self.root = root
        self.root.title("Face Emotion Detection - Real-time Analysis")
        self.root.geometry("1200x700")
        self.root.configure(bg='#2c3e50')
        
        # Initialize detector
        self.detector = EmotionDetector()
        
        # Camera variables
        self.cap = None
        self.is_running = False
        self.current_frame = None
        
        # Statistics
        self.emotion_counts = {emotion: 0 for emotion in self.detector.emotions}
        self.total_detections = 0
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Title
        title_frame = tk.Frame(self.root, bg='#34495e', height=60)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = tk.Label(title_frame, text="Face Emotion Detection System", 
                              font=('Arial', 24, 'bold'), bg='#34495e', fg='white')
        title_label.pack(pady=10)
        
        subtitle_label = tk.Label(title_frame, text="Real-time facial emotion analysis using device camera", 
                                 font=('Arial', 10), bg='#34495e', fg='#ecf0f1')
        subtitle_label.pack()
        
        # Main content area
        content_frame = tk.Frame(self.root, bg='#2c3e50')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left side - Video feed
        video_frame = tk.Frame(content_frame, bg='#34495e', relief=tk.RAISED, borderwidth=2)
        video_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        video_title = tk.Label(video_frame, text="Live Camera Feed", 
                              font=('Arial', 14, 'bold'), bg='#34495e', fg='white')
        video_title.pack(pady=10)
        
        self.video_label = tk.Label(video_frame, bg='black')
        self.video_label.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Right side - Controls and statistics
        right_frame = tk.Frame(content_frame, bg='#2c3e50', width=300)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Control panel
        control_frame = tk.Frame(right_frame, bg='#34495e', relief=tk.RAISED, borderwidth=2)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        control_title = tk.Label(control_frame, text="Controls", 
                                font=('Arial', 12, 'bold'), bg='#34495e', fg='white')
        control_title.pack(pady=10)
        
        self.start_button = tk.Button(control_frame, text="Start Camera", 
                                      command=self.start_camera, 
                                      font=('Arial', 12, 'bold'),
                                      bg='#27ae60', fg='white', 
                                      activebackground='#2ecc71',
                                      width=15, height=2)
        self.start_button.pack(pady=5)
        
        self.stop_button = tk.Button(control_frame, text="Stop Camera", 
                                     command=self.stop_camera, 
                                     font=('Arial', 12, 'bold'),
                                     bg='#e74c3c', fg='white', 
                                     activebackground='#c0392b',
                                     width=15, height=2, state=tk.DISABLED)
        self.stop_button.pack(pady=5)
        
        screenshot_button = tk.Button(control_frame, text="Save Screenshot", 
                                     command=self.save_screenshot, 
                                     font=('Arial', 10),
                                     bg='#3498db', fg='white', 
                                     activebackground='#2980b9',
                                     width=15)
        screenshot_button.pack(pady=5)
        
        reset_stats_button = tk.Button(control_frame, text="Reset Statistics", 
                                       command=self.reset_statistics, 
                                       font=('Arial', 10),
                                       bg='#95a5a6', fg='white', 
                                       activebackground='#7f8c8d',
                                       width=15)
        reset_stats_button.pack(pady=5, padx=10, pady_bottom=10)
        
        # Statistics panel
        stats_frame = tk.Frame(right_frame, bg='#34495e', relief=tk.RAISED, borderwidth=2)
        stats_frame.pack(fill=tk.BOTH, expand=True)
        
        stats_title = tk.Label(stats_frame, text="Emotion Statistics", 
                              font=('Arial', 12, 'bold'), bg='#34495e', fg='white')
        stats_title.pack(pady=10)
        
        # Current emotion display
        self.current_emotion_label = tk.Label(stats_frame, text="Current Emotion: --", 
                                             font=('Arial', 14, 'bold'), 
                                             bg='#34495e', fg='#f39c12')
        self.current_emotion_label.pack(pady=10)
        
        self.confidence_label = tk.Label(stats_frame, text="Confidence: --", 
                                        font=('Arial', 10), 
                                        bg='#34495e', fg='white')
        self.confidence_label.pack()
        
        # Separator
        separator = tk.Frame(stats_frame, height=2, bg='#7f8c8d')
        separator.pack(fill=tk.X, padx=20, pady=15)
        
        # Detection statistics
        stats_canvas_frame = tk.Frame(stats_frame, bg='#34495e')
        stats_canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.stats_labels = {}
        for emotion in self.detector.emotions:
            frame = tk.Frame(stats_canvas_frame, bg='#34495e')
            frame.pack(fill=tk.X, pady=3)
            
            label = tk.Label(frame, text=f"{emotion}:", 
                           font=('Arial', 10), bg='#34495e', fg='white', width=10, anchor='w')
            label.pack(side=tk.LEFT)
            
            count_label = tk.Label(frame, text="0 (0.0%)", 
                                  font=('Arial', 10), bg='#34495e', fg='#ecf0f1', anchor='e')
            count_label.pack(side=tk.RIGHT)
            
            self.stats_labels[emotion] = count_label
        
        # Total detections
        separator2 = tk.Frame(stats_frame, height=1, bg='#7f8c8d')
        separator2.pack(fill=tk.X, padx=20, pady=10)
        
        self.total_label = tk.Label(stats_frame, text="Total Detections: 0", 
                                   font=('Arial', 10, 'bold'), 
                                   bg='#34495e', fg='white')
        self.total_label.pack(pady=5)
        
        # Status bar
        status_frame = tk.Frame(self.root, bg='#34495e', height=30)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = tk.Label(status_frame, text="Ready", 
                                    font=('Arial', 9), bg='#34495e', fg='#ecf0f1')
        self.status_label.pack(side=tk.LEFT, padx=10)
    
    def start_camera(self):
        """Start the camera and emotion detection"""
        if not self.is_running:
            self.cap = cv2.VideoCapture(0)
            
            if not self.cap.isOpened():
                messagebox.showerror("Error", "Could not open camera!")
                return
            
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            self.is_running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.status_label.config(text="Camera running...")
            
            # Start video thread
            self.video_thread = threading.Thread(target=self.update_frame, daemon=True)
            self.video_thread.start()
    
    def stop_camera(self):
        """Stop the camera"""
        self.is_running = False
        if self.cap:
            self.cap.release()
        
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Camera stopped")
        
        # Clear video label
        self.video_label.config(image='')
    
    def update_frame(self):
        """Update video frame continuously"""
        while self.is_running:
            if self.cap and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    # Process frame
                    processed_frame = self.process_frame(frame)
                    self.current_frame = processed_frame
                    
                    # Convert to PhotoImage
                    frame_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame_rgb)
                    
                    # Resize to fit the label
                    img = img.resize((640, 480), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(image=img)
                    
                    # Update label
                    self.video_label.config(image=photo)
                    self.video_label.image = photo
    
    def process_frame(self, frame):
        """Process frame for emotion detection"""
        faces, gray = self.detector.detect_faces(frame)
        
        for (x, y, w, h) in faces:
            face_roi = gray[y:y+h, x:x+w]
            
            # Predict emotion
            emotion, predictions = self.detector.predict_emotion(face_roi)
            
            if emotion:
                confidence = np.max(predictions)
                
                # Update statistics
                self.emotion_counts[emotion] += 1
                self.total_detections += 1
                
                # Draw on frame
                frame = self.detector.draw_emotion_info(frame, x, y, w, h, emotion, confidence, predictions)
                
                # Update GUI labels
                self.root.after(0, self.update_emotion_labels, emotion, confidence)
        
        return frame
    
    def update_emotion_labels(self, emotion, confidence):
        """Update emotion labels in GUI"""
        self.current_emotion_label.config(text=f"Current Emotion: {emotion}")
        self.confidence_label.config(text=f"Confidence: {confidence*100:.1f}%")
        
        # Update statistics
        for emo in self.detector.emotions:
            count = self.emotion_counts[emo]
            percentage = (count / self.total_detections * 100) if self.total_detections > 0 else 0
            self.stats_labels[emo].config(text=f"{count} ({percentage:.1f}%)")
        
        self.total_label.config(text=f"Total Detections: {self.total_detections}")
    
    def save_screenshot(self):
        """Save current frame as screenshot"""
        if self.current_frame is not None:
            import time
            filename = f"emotion_screenshot_{int(time.time())}.png"
            cv2.imwrite(filename, self.current_frame)
            self.status_label.config(text=f"Screenshot saved: {filename}")
            messagebox.showinfo("Success", f"Screenshot saved as {filename}")
        else:
            messagebox.showwarning("Warning", "No frame to save. Start the camera first.")
    
    def reset_statistics(self):
        """Reset emotion statistics"""
        self.emotion_counts = {emotion: 0 for emotion in self.detector.emotions}
        self.total_detections = 0
        
        for emo in self.detector.emotions:
            self.stats_labels[emo].config(text="0 (0.0%)")
        
        self.total_label.config(text="Total Detections: 0")
        self.current_emotion_label.config(text="Current Emotion: --")
        self.confidence_label.config(text="Confidence: --")
        self.status_label.config(text="Statistics reset")
    
    def on_closing(self):
        """Handle window closing"""
        self.stop_camera()
        self.root.destroy()


def main():
    """Main function to run GUI application"""
    root = tk.Tk()
    app = EmotionDetectorGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
