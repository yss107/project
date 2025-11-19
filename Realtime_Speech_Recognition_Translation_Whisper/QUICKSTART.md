# Quick Start Guide

Get started with the Whisper Real-time Speech Recognition & Translation system in minutes!

## Prerequisites

- Python 3.8 or higher
- pip package manager
- (Optional) CUDA-compatible GPU for faster processing

## Installation

### Step 1: Navigate to Project Directory

```bash
cd Realtime_Speech_Recognition_Translation_Whisper
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- PyTorch (deep learning framework)
- Transformers (HuggingFace library)
- Whisper model dependencies
- Audio processing libraries
- Translation services
- Weights & Biases (optional, for MLOps)

**Note:** The first run will download the Whisper Large V3 model (~3GB). This is a one-time download.

### Step 3 (Optional): Set up Weights & Biases

If you want to track your experiments:

```bash
# Sign up at https://wandb.ai and get your API key
wandb login

# Or set environment variable
export WANDB_API_KEY=your_api_key_here
```

## Quick Test

### Test Translation (No Model Required)

```bash
python quick_demo.py
```

This tests the translation functionality without downloading the large Whisper model.

### Test Setup

```bash
python test_setup.py
```

This verifies all dependencies are installed correctly.

## Usage Examples

### 1. Real-time Speech Recognition (Basic)

```bash
python realtime_speech_translator.py
```

This will:
1. Load the Whisper Large V3 model (first time only)
2. Start listening to your microphone
3. Transcribe speech in real-time
4. Translate to Spanish (default)
5. Display results

**Controls:**
- Speak naturally into your microphone
- Press `Ctrl+C` to stop

### 2. Interactive Examples

```bash
python example_usage.py
```

Choose from multiple examples:
1. Basic transcription (no translation)
2. Spanish translation
3. French translation
4. German translation
5. W&B logging
6. Fast response mode
7. Continuous recording
8. CPU-only mode
9. Multiple languages demo

### 3. Batch Processing

Process audio files:

```bash
# Single file
python batch_transcriber.py audio.wav

# With translation to Spanish
python batch_transcriber.py audio.wav --target-language es

# Process entire directory
python batch_transcriber.py /path/to/audio/folder --target-language fr --output results.json
```

### 4. Jupyter Notebook

```bash
jupyter notebook Whisper_Realtime_Demo.ipynb
```

Interactive exploration with step-by-step examples.

## Configuration

### Change Target Language

Edit `realtime_speech_translator.py`:

```python
TARGET_LANGUAGE = "fr"  # French
# Options: es, fr, de, it, pt, ru, ja, zh, ko, ar, etc.
```

### Adjust Audio Chunk Size

For faster response (less context):
```python
chunk_duration=3.0  # 3 seconds
```

For better accuracy (more context):
```python
chunk_duration=10.0  # 10 seconds
```

### Force CPU Mode

If you don't have a GPU:
```python
device="cpu"
```

## Common Issues

### Issue: "No module named 'torch'"

**Solution:** Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: "No module named 'pyaudio'" or audio errors

**Solution:** Install system audio libraries

**Ubuntu/Debian:**
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio
```

**macOS:**
```bash
brew install portaudio
pip install pyaudio
```

**Windows:**
```bash
pip install pipwin
pipwin install pyaudio
```

### Issue: "CUDA out of memory"

**Solution:** Use CPU mode or reduce batch size
```python
device="cpu"  # In realtime_speech_translator.py
```

### Issue: Microphone not detected

**Solution:** Check permissions and list devices
```python
import sounddevice as sd
print(sd.query_devices())
```

### Issue: Poor transcription quality

**Solutions:**
1. Speak clearly and at moderate pace
2. Reduce background noise
3. Use a good quality microphone
4. Increase chunk duration for more context
5. Check microphone volume levels

## Next Steps

1. **Customize for your use case**: Edit the scripts to match your requirements
2. **Integrate with your app**: Import the `WhisperRealtimeTranslator` class
3. **Monitor with W&B**: Enable Weights & Biases for experiment tracking
4. **Optimize performance**: Tune chunk duration and batch size
5. **Add more languages**: Extend translation to multiple target languages

## Architecture Overview

```
User speaks → Microphone → Audio Stream → Whisper Model
                                              ↓
                                         Transcription
                                              ↓
                                         Translator
                                              ↓
                                      Display Results
                                              ↓
                                     (Optional) W&B Logging
```

## Performance Tips

1. **GPU Acceleration**: Use CUDA-enabled GPU for 5-10x speedup
2. **Chunk Size**: Balance between latency and accuracy
3. **Model Selection**: Use base/small models for faster processing
4. **Batch Processing**: Process multiple files efficiently
5. **Audio Quality**: Use good quality audio for best results

## Resources

- [Full Documentation](README.md)
- [Example Scripts](example_usage.py)
- [Whisper Model Card](https://huggingface.co/openai/whisper-large-v3)
- [W&B Documentation](https://docs.wandb.ai/)

## Support

For issues or questions:
1. Check the [README.md](README.md) troubleshooting section
2. Run `python test_setup.py` to diagnose issues
3. Open an issue on GitHub

## License

MIT License - See LICENSE file for details

---

**Ready to start? Run:** `python realtime_speech_translator.py`
