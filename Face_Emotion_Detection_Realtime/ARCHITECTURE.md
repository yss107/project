# System Architecture

## Overview

The Face Emotion Detection system consists of three main components:

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                      │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │  OpenCV Window   │         │   Tkinter GUI    │         │
│  │  (Simple Mode)   │         │  (Advanced Mode) │         │
│  └────────┬─────────┘         └────────┬─────────┘         │
│           │                            │                    │
└───────────┼────────────────────────────┼────────────────────┘
            │                            │
            └──────────┬─────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              Emotion Detection Layer                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────┐            │
│  │          EmotionDetector Class              │            │
│  ├─────────────────────────────────────────────┤            │
│  │                                             │            │
│  │  • Face Detection (Haar Cascade)           │            │
│  │  • Emotion Prediction (CNN Model)          │            │
│  │  • Visualization & Statistics              │            │
│  │                                             │            │
│  └───────────────┬─────────────────────────────┘            │
│                  │                                           │
└──────────────────┼───────────────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────────────────┐
│                   Core Components                            │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐    │
│  │   OpenCV     │   │  TensorFlow  │   │   Dataset    │    │
│  │              │   │              │   │              │    │
│  │ • Camera I/O │   │ • CNN Model  │   │ • Training   │    │
│  │ • Face Det.  │   │ • Inference  │   │ • Validation │    │
│  │ • Display    │   │ • Training   │   │              │    │
│  └──────────────┘   └──────────────┘   └──────────────┘    │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

## Data Flow

### Real-time Detection Pipeline

```
Camera Capture → Frame Processing → Face Detection → 
Emotion Prediction → Visualization → Display

Detailed Flow:
1. Camera Capture (640x480 RGB)
   ↓
2. Convert to Grayscale
   ↓
3. Face Detection (Haar Cascade)
   ↓
4. Face ROI Extraction
   ↓
5. Resize to 48x48
   ↓
6. Normalize (0-1)
   ↓
7. CNN Model Inference
   ↓
8. Softmax Output (7 classes)
   ↓
9. Visualization
   - Draw bounding box
   - Display emotion label
   - Show confidence
   - Draw probability bars
   ↓
10. Display Frame
```

## CNN Model Architecture

```
Input: 48x48x1 (Grayscale Image)
    ↓
┌───────────────────────────────┐
│   Convolutional Block 1       │
│   • Conv2D (32 filters)       │
│   • BatchNormalization        │
│   • Conv2D (64 filters)       │
│   • BatchNormalization        │
│   • MaxPooling2D (2x2)        │
│   • Dropout (0.25)            │
└───────────┬───────────────────┘
            ↓
┌───────────────────────────────┐
│   Convolutional Block 2       │
│   • Conv2D (128 filters)      │
│   • BatchNormalization        │
│   • Conv2D (128 filters)      │
│   • BatchNormalization        │
│   • MaxPooling2D (2x2)        │
│   • Dropout (0.25)            │
└───────────┬───────────────────┘
            ↓
┌───────────────────────────────┐
│   Convolutional Block 3       │
│   • Conv2D (256 filters)      │
│   • BatchNormalization        │
│   • MaxPooling2D (2x2)        │
│   • Dropout (0.25)            │
└───────────┬───────────────────┘
            ↓
┌───────────────────────────────┐
│   Fully Connected Layers      │
│   • Flatten                   │
│   • Dense (512 units, ReLU)   │
│   • BatchNormalization        │
│   • Dropout (0.5)             │
│   • Dense (256 units, ReLU)   │
│   • BatchNormalization        │
│   • Dropout (0.5)             │
│   • Dense (7 units, Softmax)  │
└───────────┬───────────────────┘
            ↓
Output: [P(Angry), P(Disgust), P(Fear), P(Happy), 
         P(Neutral), P(Sad), P(Surprise)]
```

## Training Pipeline

```
┌─────────────────────────────────────────────────────────┐
│                    Training Process                      │
└─────────────────────────────────────────────────────────┘

1. Data Loading
   ├── CSV Format (Kaggle)
   │   • emotion: 0-6
   │   • pixels: space-separated values
   │
   └── Directory Structure
       • angry/image1.jpg
       • happy/image2.jpg
       • etc.
       ↓
2. Data Preprocessing
   ├── Reshape to 48x48x1
   ├── Normalize (0-1)
   └── One-hot encode labels
       ↓
3. Data Split
   ├── Training (80%)
   └── Validation (20%)
       ↓
4. Data Augmentation (Optional)
   ├── Rotation (±15°)
   ├── Width/Height Shift (±10%)
   ├── Horizontal Flip
   └── Zoom (±10%)
       ↓
5. Model Training
   ├── Optimizer: Adam
   ├── Loss: Categorical Crossentropy
   ├── Metrics: Accuracy
   │
   ├── Callbacks:
   │   ├── ModelCheckpoint (save best)
   │   ├── EarlyStopping (patience=10)
   │   └── ReduceLROnPlateau (patience=5)
   │
   └── Epochs: 50 (configurable)
       ↓
6. Model Evaluation
   ├── Classification Report
   ├── Confusion Matrix
   └── Accuracy/Loss Plots
       ↓
7. Model Saving
   ├── emotion_model_best.h5
   └── emotion_model_final.h5
```

## Emotion Classification

```
┌────────────────────────────────────────────────────────┐
│                  Emotion Classes                       │
├────────────────────────────────────────────────────────┤
│                                                        │
│  0: Angry    → Furrowed brows, tight lips            │
│  1: Disgust  → Wrinkled nose, raised upper lip       │
│  2: Fear     → Wide eyes, raised eyebrows            │
│  3: Happy    → Smile, raised cheeks                  │
│  4: Neutral  → Relaxed face                          │
│  5: Sad      → Downturned mouth, drooping eyes       │
│  6: Surprise → Wide eyes, open mouth                 │
│                                                        │
└────────────────────────────────────────────────────────┘
```

## File Structure

```
Face_Emotion_Detection_Realtime/
│
├── Core Files
│   ├── emotion_detector.py          # Main detector class
│   ├── emotion_detector_gui.py      # GUI application
│   └── train_model.py               # Training script
│
├── Utility Files
│   ├── demo.py                      # Demo/test script
│   ├── examples.py                  # Usage examples
│   └── test_structure.py            # Structure validation
│
├── Configuration
│   ├── requirements.txt             # Dependencies
│   └── setup.sh                     # Setup script
│
└── Documentation
    ├── README.md                    # Main documentation
    ├── QUICKSTART.md                # Quick start guide
    └── ARCHITECTURE.md              # This file
```

## Integration Points

### 1. Custom Model Integration

```python
# Use your own trained model
detector = EmotionDetector(model_path='path/to/model.h5')
```

### 2. Custom Emotion Mapping

```python
# Modify emotion labels
detector.emotions = ['Custom1', 'Custom2', ...]
```

### 3. Custom Callbacks

```python
def on_emotion_detected(emotion, confidence):
    # Your custom logic
    pass

# Integrate into detection loop
```

## Performance Considerations

1. **Frame Rate**: ~30 FPS on modern hardware
2. **Latency**: 20-30ms per face detection + inference
3. **Memory**: ~500MB with model loaded
4. **CPU Usage**: 15-30% per core
5. **GPU Support**: Available with CUDA-enabled TensorFlow

## Security & Privacy

- All processing is done locally
- No data is sent to external servers
- Camera feed is not recorded by default
- Screenshots are saved only when explicitly requested

## Extensibility

The system is designed to be extensible:

1. **New Models**: Easy to plug in different architectures
2. **New Features**: Modular design allows adding features
3. **Multiple Cameras**: Can be extended for multiple inputs
4. **Video Files**: Can process pre-recorded videos
5. **Batch Processing**: Can be adapted for batch processing

## Dependencies Graph

```
Application Layer
    ├── tkinter (GUI)
    ├── PIL (Image processing)
    └── opencv-python (Video & Display)
            ↓
Processing Layer
    ├── tensorflow (Deep Learning)
    ├── numpy (Array operations)
    └── opencv-python (Face detection)
            ↓
Training Layer
    ├── tensorflow (Model training)
    ├── pandas (Data loading)
    ├── matplotlib (Visualization)
    ├── seaborn (Advanced plots)
    └── scikit-learn (Metrics)
```

---

For more information, see the main [README.md](README.md)
