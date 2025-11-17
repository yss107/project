# Quick Start Guide

## Installation in 3 Steps

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

Or use the setup script:
```bash
bash setup.sh
```

### Step 2: Test Installation

```bash
python3 demo.py
```

This will verify that your camera works and all dependencies are installed.

### Step 3: Run the Application

**Option A: Simple Interface**
```bash
python3 emotion_detector.py
```
- Press 'q' to quit
- Press 's' to save screenshot

**Option B: GUI Interface (Recommended)**
```bash
python3 emotion_detector_gui.py
```
- User-friendly interface with buttons
- Real-time statistics
- Easy screenshot saving

---

## Common Issues

### Camera Not Working
- Check if camera is connected
- Grant camera permissions
- Try different camera index: `cap = cv2.VideoCapture(1)`

### Dependencies Error
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Low Accuracy
The model needs training! See the Training section in README.md

---

## Training Your Model

1. Download the dataset from [Kaggle](https://www.kaggle.com/datasets/samithsachidanandan/human-face-emotions)

2. Run the training script:
```bash
python3 train_model.py
```

3. Follow the prompts to select dataset format and parameters

4. The trained model will be saved as `emotion_model_best.h5`

5. Use the trained model by updating the code:
```python
detector = EmotionDetector(model_path='emotion_model_best.h5')
```

---

## Tips for Best Results

1. **Good Lighting**: Ensure your face is well-lit
2. **Face the Camera**: Look directly at the camera
3. **Clear Expressions**: Make clear facial expressions
4. **Distance**: Stay 1-2 feet from the camera
5. **Train the Model**: For accurate results, train on the full dataset

---

## Next Steps

- Train your own model with the Kaggle dataset
- Experiment with different expressions
- Track your emotions over time
- Share your results!

For detailed documentation, see [README.md](README.md)
