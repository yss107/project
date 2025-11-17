# Face Emotion Detection - Real-time Analysis

A real-time face emotion detection system that uses your device camera to analyze facial emotions. This project is based on the [Kaggle Human Face Emotions Dataset](https://www.kaggle.com/datasets/samithsachidanandan/human-face-emotions).

## Features

- **Real-time emotion detection** from webcam feed
- **7 emotion categories**: Angry, Disgust, Fear, Happy, Neutral, Sad, Surprise
- **Two interfaces**:
  - Simple OpenCV-based interface
  - Advanced GUI with statistics and controls
- **Deep learning model** using CNN architecture
- **Visual feedback** with emotion labels, confidence scores, and probability bars
- **Statistics tracking** to monitor emotion distribution
- **Screenshot capability** to save moments

## Demo

The system detects faces in real-time and displays:
- Bounding box around detected faces
- Predicted emotion with confidence percentage
- Emotion probability distribution (bar chart)
- Live statistics of detected emotions

## Installation

### Prerequisites

- Python 3.8 or higher
- Webcam/camera device
- (Optional) GPU for faster processing

### Setup

1. Clone the repository or navigate to the project directory:
```bash
cd Face_Emotion_Detection_Realtime
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

### Quick Start - Simple Interface

Run the basic emotion detector with OpenCV interface:

```bash
python emotion_detector.py
```

**Controls:**
- Press `q` to quit
- Press `s` to save a screenshot

### GUI Interface (Recommended)

Run the advanced GUI version with better controls and statistics:

```bash
python emotion_detector_gui.py
```

**Features:**
- Start/Stop camera buttons
- Real-time emotion statistics
- Save screenshots
- Reset statistics
- Visual emotion probability display

## Training Your Own Model

The project includes a training script to train the model on the Kaggle dataset.

### Dataset Preparation

1. Download the dataset from [Kaggle](https://www.kaggle.com/datasets/samithsachidanandan/human-face-emotions)

2. The dataset can be in two formats:
   - **CSV format**: Single file with 'emotion' and 'pixels' columns
   - **Directory structure**: Folders named after emotions containing images

### Training

```bash
python train_model.py
```

Follow the interactive prompts to:
1. Select dataset format (CSV or directory)
2. Set training parameters (epochs, batch size)
3. Enable/disable data augmentation

The script will:
- Train the model with the specified parameters
- Save the best model (`emotion_model_best.h5`)
- Generate training history plots
- Create a confusion matrix
- Evaluate model performance

### Using a Trained Model

To use your trained model, modify the `EmotionDetector` initialization:

```python
detector = EmotionDetector(model_path='emotion_model_best.h5')
```

## Project Structure

```
Face_Emotion_Detection_Realtime/
├── emotion_detector.py          # Core detection module with OpenCV interface
├── emotion_detector_gui.py      # GUI application with tkinter
├── train_model.py               # Model training script
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Model Architecture

The emotion detection model uses a Convolutional Neural Network (CNN) with:
- 3 convolutional blocks with batch normalization
- MaxPooling and Dropout layers for regularization
- Fully connected layers for classification
- Input: 48x48 grayscale images
- Output: 7 emotion classes with softmax activation

### Architecture Details:
- **Input Layer**: 48x48x1 (grayscale image)
- **Conv Block 1**: 32 & 64 filters, 3x3 kernels
- **Conv Block 2**: 128 & 128 filters, 3x3 kernels
- **Conv Block 3**: 256 filters, 3x3 kernels
- **Dense Layers**: 512 & 256 units with dropout
- **Output Layer**: 7 units (softmax)

## Technical Details

### Emotion Classes

The system recognizes 7 basic emotions:
1. **Angry**: Furrowed brows, tight lips
2. **Disgust**: Wrinkled nose, raised upper lip
3. **Fear**: Wide eyes, raised eyebrows
4. **Happy**: Smile, raised cheeks
5. **Neutral**: Relaxed face, no strong expression
6. **Sad**: Downturned mouth, drooping eyes
7. **Surprise**: Wide eyes, open mouth, raised eyebrows

### Face Detection

- Uses **Haar Cascade Classifier** for face detection
- Processes frames in grayscale for efficiency
- Detects multiple faces simultaneously

### Performance

- **Real-time processing**: ~30 FPS on modern hardware
- **Model size**: ~10-15 MB
- **Inference time**: ~20-30ms per face

## Troubleshooting

### Camera Not Opening

```python
# Check camera index (try 0, 1, 2, etc.)
cap = cv2.VideoCapture(1)  # Instead of 0
```

### Low FPS

- Reduce camera resolution
- Close other applications
- Use GPU acceleration (requires CUDA-enabled TensorFlow)

### Model Not Found

If you see "Using untrained model" warning:
- Train your own model using `train_model.py`
- Download a pre-trained model (if available)
- Specify the model path when initializing

### Import Errors

```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

## Dataset Information

**Source**: [Kaggle - Human Face Emotions Dataset](https://www.kaggle.com/datasets/samithsachidanandan/human-face-emotions)

**Dataset Structure**:
- 48x48 pixel grayscale images
- 7 emotion categories
- Thousands of labeled examples
- Suitable for training deep learning models

## Future Enhancements

- [ ] Add support for video file input
- [ ] Implement emotion tracking over time
- [ ] Add emotion intensity detection
- [ ] Support for multiple face tracking
- [ ] Export emotion data to CSV/JSON
- [ ] Add custom emotion mapping
- [ ] Implement facial landmark detection
- [ ] Add age and gender estimation

## Dependencies

- **OpenCV**: Camera access and face detection
- **TensorFlow/Keras**: Deep learning model
- **NumPy**: Array operations
- **Pillow**: Image processing for GUI
- **Pandas**: Data handling for training
- **Matplotlib**: Visualization
- **Scikit-learn**: Model evaluation
- **Seaborn**: Enhanced visualizations

## Performance Tips

1. **Lighting**: Ensure good lighting for better detection
2. **Distance**: Keep face 1-2 feet from camera
3. **Angle**: Face the camera directly for best results
4. **Expression**: Make clear expressions for accurate detection

## Credits

- Dataset: Samith Sachidanandan (Kaggle)
- Face Detection: OpenCV Haar Cascades
- Deep Learning: TensorFlow/Keras

## License

This project is open-source and available for educational purposes.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## Author

Created as part of a machine learning project collection.

## Support

For issues, questions, or contributions, please refer to the main project repository.

---

**Note**: This project uses a pre-defined CNN architecture. For best results, train the model on the Kaggle dataset before using it for real-time detection. The untrained model will not provide accurate predictions.
