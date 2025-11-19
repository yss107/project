# Extended Features Documentation

## Overview

This document describes the new extended features added to the Whisper Real-time Speech Recognition & Translation system.

## Features Implemented

### ✅ 1. Web Interface with FastAPI

A complete web application with REST API and interactive web UI.

**Key Features:**
- RESTful API endpoints for transcription and translation
- Interactive web interface accessible via browser
- Real-time WebSocket support for streaming audio
- Multiple language translation in a single request
- Subtitle export (SRT/VTT formats)
- CORS support for cross-origin requests
- Auto-generated API documentation (OpenAPI/Swagger)

**Usage:**

```bash
# Start the web server
python extended_translator.py --mode web --web-port 8000

# Or directly
python web_api.py
```

**Access:**
- Web UI: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

**API Endpoints:**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web UI interface |
| `/health` | GET | Health check |
| `/transcribe` | POST | Transcribe single audio file |
| `/transcribe/multiple` | POST | Transcribe with multiple languages |
| `/export/subtitle` | POST | Export subtitles (SRT/VTT) |
| `/ws/transcribe` | WebSocket | Real-time streaming |

### ✅ 2. WebSocket Support for Streaming

Real-time bidirectional communication for live audio streaming.

**Features:**
- Binary audio data streaming
- Real-time transcription and translation
- Low-latency processing
- Automatic reconnection handling
- Multiple concurrent connections

**Usage (JavaScript):**

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/transcribe');

ws.onopen = () => {
    console.log('Connected');
    // Send audio data
    ws.send(audioBlob);
};

ws.onmessage = (event) => {
    const result = JSON.parse(event.data);
    console.log('Transcription:', result.transcription);
    console.log('Translations:', result.translations);
};
```

### ✅ 3. Multiple Language Translation Simultaneously

Translate transcribed text to multiple languages in a single request.

**Features:**
- Parallel translation to multiple languages
- Support for 100+ languages via Google Translate
- Efficient batch processing
- Configurable language selection

**Usage (Python):**

```python
from extended_translator import ExtendedWhisperTranslator

translator = ExtendedWhisperTranslator(
    target_languages=["es", "fr", "de", "ja"]  # Spanish, French, German, Japanese
)

# Translations will be returned for all specified languages
```

**Usage (CLI):**

```bash
python extended_translator.py --mode file --file audio.wav \
    --languages es fr de it pt
```

**Supported Languages:**
- `es` - Spanish
- `fr` - French
- `de` - German
- `it` - Italian
- `pt` - Portuguese
- `ru` - Russian
- `ja` - Japanese
- `zh` - Chinese
- `ko` - Korean
- `ar` - Arabic
- And 90+ more...

### ✅ 4. Custom Vocabulary Support

Improve recognition accuracy for domain-specific terms.

**Features:**
- Custom word/phrase dictionary
- Case-insensitive matching
- Automatic replacement in transcriptions
- Useful for technical terms, brand names, proper nouns

**Usage (Python):**

```python
translator = ExtendedWhisperTranslator(
    custom_vocabulary=["TensorFlow", "PyTorch", "Kubernetes", "API"]
)
```

**Usage (CLI):**

```bash
python extended_translator.py --mode realtime \
    --vocabulary "OpenAI" "GPT-4" "Whisper" "FastAPI"
```

### ✅ 5. Speaker Diarization

Identify and label different speakers in audio.

**Features:**
- Automatic speaker detection
- Timestamp-based speaker segments
- Configurable number of speakers
- Speaker clustering using acoustic features
- Label smoothing to reduce rapid switching

**Usage (Python):**

```python
from speaker_diarization import SpeakerDiarizer, diarize_audio_file

# Diarize audio file
segments = diarize_audio_file("audio.wav", n_speakers=2)

for segment in segments:
    print(f"{segment['speaker']}: {segment['start']:.1f}s - {segment['end']:.1f}s")
```

**Usage (CLI):**

```bash
python extended_translator.py --mode file --file audio.wav \
    --speaker-diarization
```

**Output Example:**
```
Speaker_0: 0.0s - 5.2s (duration: 5.2s)
Speaker_1: 5.2s - 10.4s (duration: 5.2s)
Speaker_0: 10.4s - 15.0s (duration: 4.6s)
```

### ✅ 6. Emotion Detection

Analyze and detect emotional tone from speech.

**Features:**
- Detect 5 basic emotions: neutral, happy, sad, angry, fear
- Prosodic feature extraction (pitch, energy, spectral features)
- Confidence scores for predictions
- Real-time emotion analysis

**Detected Emotions:**
- **Neutral**: Calm, regular speech
- **Happy**: High energy, elevated pitch variation
- **Sad**: Low energy, lower pitch
- **Angry**: High energy, high zero-crossing rate
- **Fear**: High pitch variation

**Usage (Python):**

```python
from speaker_diarization import EmotionDetector

detector = EmotionDetector(sample_rate=16000)
emotion_result = detector.detect_emotion(audio_data)

print(f"Emotion: {emotion_result['emotion']}")
print(f"Confidence: {emotion_result['confidence']:.2f}")
```

**Usage (CLI):**

```bash
python extended_translator.py --mode file --file audio.wav \
    --emotion-detection
```

**Output Example:**
```
😊 Detected Emotion: Happy (confidence: 0.73)
```

### ✅ 7. Audio Enhancement Preprocessing

Improve audio quality before transcription.

**Features:**
- **Noise Reduction**: Spectral gating to remove background noise
- **Normalization**: Adjust audio levels for consistent processing
- **High-pass Filtering**: Remove low-frequency rumble
- **Voice Activity Detection**: Trim silence from audio
- **Resampling**: Convert to target sample rate

**Usage (Python):**

```python
from audio_enhancement import AudioEnhancer, preprocess_audio_file

# Load and enhance audio
audio_data, sr = preprocess_audio_file(
    "noisy_audio.wav",
    sample_rate=16000,
    enhance=True
)

# Or use enhancer directly
enhancer = AudioEnhancer(sample_rate=16000)
clean_audio = enhancer.enhance_audio(noisy_audio)
```

**Usage (CLI):**

```bash
# Audio enhancement is enabled by default
python extended_translator.py --mode file --file audio.wav --enhance-audio
```

**Enhancement Pipeline:**
1. Convert to mono (if stereo)
2. Spectral noise reduction
3. Audio normalization
4. High-pass filtering (remove <80 Hz)
5. Voice activity detection and silence trimming

### ✅ 8. Export to Subtitle Formats (SRT, VTT)

Generate subtitle files from transcriptions.

**Features:**
- SRT (SubRip) format support
- WebVTT format support
- Timestamp synchronization
- Support for translated subtitles
- Chunked subtitles with proper timing

**SRT Format:**
```
1
00:00:00,000 --> 00:00:05,000
This is the first subtitle

2
00:00:05,000 --> 00:00:10,000
This is the second subtitle
```

**WebVTT Format:**
```
WEBVTT

00:00:00.000 --> 00:00:05.000
This is the first subtitle

00:00:05.000 --> 00:00:10.000
This is the second subtitle
```

**Usage (Python):**

```python
from web_api import generate_srt_subtitle, generate_vtt_subtitle

# Generate SRT
srt_content = generate_srt_subtitle(transcription_data, text)
with open('subtitles.srt', 'w') as f:
    f.write(srt_content)

# Generate VTT
vtt_content = generate_vtt_subtitle(transcription_data, text)
with open('subtitles.vtt', 'w') as f:
    f.write(vtt_content)
```

**Usage (CLI):**

```bash
# Export SRT
python extended_translator.py --mode file --file audio.wav \
    --export-subtitle srt

# Export VTT
python extended_translator.py --mode file --file audio.wav \
    --export-subtitle vtt
```

**Usage (Web API):**

```bash
# Via curl
curl -X POST "http://localhost:8000/export/subtitle" \
    -H "Content-Type: application/json" \
    -d '{"transcription_data": {...}, "format": "srt"}'
```

## Complete Example

Here's how to use all features together:

```bash
python extended_translator.py \
    --mode file \
    --file conversation.wav \
    --languages es fr de ja \
    --enhance-audio \
    --speaker-diarization \
    --emotion-detection \
    --vocabulary "OpenAI" "Whisper" "GPT-4" \
    --export-subtitle srt
```

This will:
1. ✅ Load and enhance the audio file
2. ✅ Transcribe with Whisper Large V3
3. ✅ Apply custom vocabulary
4. ✅ Translate to Spanish, French, German, and Japanese
5. ✅ Identify different speakers
6. ✅ Detect emotions in speech
7. ✅ Export as SRT subtitle file

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Extended Whisper System                  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────┐         ┌─────────────────┐           │
│  │   Audio Input   │────────▶│ Audio Enhancer  │           │
│  │ (Mic/File/Web)  │         │  - Noise reduce │           │
│  └─────────────────┘         │  - Normalize    │           │
│                               │  - Filter       │           │
│                               └────────┬────────┘           │
│                                        │                     │
│                                        ▼                     │
│                               ┌─────────────────┐           │
│                               │ Whisper Model   │           │
│                               │ (Large V3)      │           │
│                               └────────┬────────┘           │
│                                        │                     │
│                    ┌───────────────────┼───────────────┐   │
│                    │                   │               │   │
│                    ▼                   ▼               ▼   │
│           ┌─────────────┐    ┌──────────────┐ ┌────────┐  │
│           │   Multi-    │    │   Speaker    │ │Emotion │  │
│           │  Language   │    │ Diarization  │ │Detector│  │
│           │ Translation │    └──────────────┘ └────────┘  │
│           └──────┬──────┘                                   │
│                  │                                          │
│                  ▼                                          │
│           ┌─────────────┐                                   │
│           │   Output    │                                   │
│           │ - JSON/Text │                                   │
│           │ - Subtitles │                                   │
│           │ - Web UI    │                                   │
│           └─────────────┘                                   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Performance Considerations

- **Audio Enhancement**: Adds ~0.1-0.5s processing time
- **Speaker Diarization**: Adds ~1-3s for 30s audio
- **Emotion Detection**: Adds ~0.1-0.2s processing time
- **Multiple Languages**: Linear with number of languages (~0.5s per language)

**Recommendations:**
- Use GPU for faster transcription
- Disable unused features for better performance
- Use shorter audio chunks for real-time applications
- Consider async processing for batch operations

## Installation

Update your requirements:

```bash
pip install -r requirements.txt
```

New dependencies added:
- `fastapi>=0.104.0` - Web API framework
- `uvicorn[standard]>=0.24.0` - ASGI server
- `python-multipart>=0.0.6` - File upload support
- `websockets>=12.0` - WebSocket support

## Testing

Test each feature individually:

```bash
# Test audio enhancement
python audio_enhancement.py

# Test speaker diarization and emotion detection
python speaker_diarization.py

# Test web API
python web_api.py
# Then visit http://localhost:8000

# Test complete system
python extended_translator.py --mode realtime
```

## Future Enhancements

Potential additions:
- [ ] Real-time speaker identification with pre-trained models
- [ ] Advanced emotion detection with deep learning
- [ ] Background noise profile learning
- [ ] Multi-channel audio support
- [ ] Video subtitle overlay
- [ ] Live streaming integration
- [ ] Mobile app support
- [ ] Cloud deployment templates

## Troubleshooting

**Issue**: Web API won't start
```bash
# Solution: Check if port is available
sudo netstat -tulpn | grep 8000
# Use different port
python extended_translator.py --mode web --web-port 8080
```

**Issue**: Audio enhancement not working
```bash
# Solution: Check scipy installation
pip install --upgrade scipy
```

**Issue**: WebSocket connection fails
```bash
# Solution: Check CORS settings and firewall
# Allow port in firewall
sudo ufw allow 8000
```

## License

This extension maintains the MIT License of the original project.

## Acknowledgments

- OpenAI Whisper for state-of-the-art speech recognition
- FastAPI for modern web framework
- SciPy for signal processing
- HuggingFace for model hosting
