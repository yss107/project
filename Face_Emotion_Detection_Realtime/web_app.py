"""
Web Interface for Face Emotion Detection
Provides a modern, real-time web-based interface for emotion detection
"""

import cv2
import numpy as np
import base64
import json
from flask import Flask, render_template, Response, jsonify
from flask_socketio import SocketIO, emit
import threading
import time
from emotion_detector import EmotionDetector
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'emotion_detection_secret_key_2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables
detector = EmotionDetector()
camera = None
camera_lock = threading.Lock()
is_camera_running = False
emotion_history = []
emotion_stats = {emotion: 0 for emotion in detector.emotions}
total_frames = 0


def generate_frames():
    """Generate frames from camera for video streaming"""
    global camera, is_camera_running, emotion_history, emotion_stats, total_frames
    
    while is_camera_running:
        with camera_lock:
            if camera is None or not camera.isOpened():
                break
                
            success, frame = camera.read()
            if not success:
                break
            
            # Detect faces and emotions
            faces, gray = detector.detect_faces(frame)
            
            detected_emotions = []
            for (x, y, w, h) in faces:
                face_roi = gray[y:y+h, x:x+w]
                emotion, predictions = detector.predict_emotion(face_roi)
                
                if emotion:
                    confidence = np.max(predictions)
                    detected_emotions.append({
                        'emotion': emotion,
                        'confidence': float(confidence),
                        'predictions': {detector.emotions[i]: float(predictions[i]) 
                                       for i in range(len(predictions))}
                    })
                    
                    # Draw on frame
                    frame = detector.draw_emotion_info(frame, x, y, w, h, emotion, confidence, predictions)
                    
                    # Update statistics
                    emotion_stats[emotion] += 1
                    total_frames += 1
                    
                    # Add to history (keep last 100)
                    emotion_history.append({
                        'emotion': emotion,
                        'confidence': float(confidence),
                        'timestamp': datetime.now().isoformat()
                    })
                    if len(emotion_history) > 100:
                        emotion_history.pop(0)
            
            # Emit real-time data via WebSocket
            if detected_emotions:
                socketio.emit('emotion_update', {
                    'emotions': detected_emotions,
                    'stats': emotion_stats,
                    'total': total_frames,
                    'timestamp': datetime.now().isoformat()
                })
            
            # Encode frame
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        time.sleep(0.03)  # ~30 FPS


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/api/start_camera', methods=['POST'])
def start_camera():
    """Start the camera"""
    global camera, is_camera_running
    
    with camera_lock:
        if not is_camera_running:
            camera = cv2.VideoCapture(0)
            if not camera.isOpened():
                return jsonify({'success': False, 'error': 'Could not open camera'}), 500
            
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            camera.set(cv2.CAP_PROP_FPS, 30)
            
            is_camera_running = True
            
            # Start frame generation in a separate thread
            threading.Thread(target=generate_frames, daemon=True).start()
            
            return jsonify({'success': True, 'message': 'Camera started'})
        else:
            return jsonify({'success': False, 'error': 'Camera already running'}), 400


@app.route('/api/stop_camera', methods=['POST'])
def stop_camera():
    """Stop the camera"""
    global camera, is_camera_running
    
    with camera_lock:
        is_camera_running = False
        if camera:
            camera.release()
            camera = None
        
        return jsonify({'success': True, 'message': 'Camera stopped'})


@app.route('/api/stats')
def get_stats():
    """Get emotion statistics"""
    return jsonify({
        'stats': emotion_stats,
        'total': total_frames,
        'history': emotion_history[-20:] if emotion_history else []
    })


@app.route('/api/reset_stats', methods=['POST'])
def reset_stats():
    """Reset statistics"""
    global emotion_stats, emotion_history, total_frames
    
    emotion_stats = {emotion: 0 for emotion in detector.emotions}
    emotion_history = []
    total_frames = 0
    
    return jsonify({'success': True, 'message': 'Statistics reset'})


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('connection_response', {'status': 'connected'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')


def main():
    """Run the web application"""
    print("=" * 60)
    print("Face Emotion Detection - Web Interface")
    print("=" * 60)
    print("\nStarting web server...")
    print("Open your browser and navigate to: http://localhost:5000")
    print("\nPress CTRL+C to stop the server")
    print("=" * 60)
    
    try:
        socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        print("\nShutting down...")
        if camera:
            camera.release()


if __name__ == '__main__':
    main()
