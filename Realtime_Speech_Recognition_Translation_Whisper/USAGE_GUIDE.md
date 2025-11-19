# Quick Start Guide for Extended Features

## Installation

1. Navigate to the project directory:
```bash
cd Realtime_Speech_Recognition_Translation_Whisper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your settings
```

## Usage Examples

### 1. Web Interface (Recommended for Beginners)

Start the web server:
```bash
python extended_translator.py --mode web --web-port 8000
```

Then open your browser:
- Web UI: http://localhost:8000
- API Docs: http://localhost:8000/docs

**Features available in Web UI:**
- Upload audio files for transcription
- Select multiple target languages
- Real-time WebSocket streaming
- Export subtitles (SRT/VTT)
- View transcriptions and translations

### 2. File Processing

**Basic transcription:**
```bash
python extended_translator.py --mode file --file audio.wav
```

**Multiple languages:**
```bash
python extended_translator.py --mode file --file audio.wav \
    --languages es fr de it
```

**With all features:**
```bash
python extended_translator.py --mode file --file audio.wav \
    --languages es fr de ja \
    --enhance-audio \
    --speaker-diarization \
    --emotion-detection \
    --vocabulary "OpenAI" "Whisper" "GPT" \
    --export-subtitle srt
```

### 3. Real-time Recording

**Basic real-time:**
```bash
python extended_translator.py --mode realtime
```

**With enhancements:**
```bash
python extended_translator.py --mode realtime \
    --languages es fr \
    --enhance-audio \
    --emotion-detection
```

## Feature-Specific Examples

### Audio Enhancement
```bash
# Automatically enabled for better quality
python extended_translator.py --mode file --file noisy_audio.wav --enhance-audio
```

### Speaker Diarization
```bash
# Identify different speakers in a conversation
python extended_translator.py --mode file --file conversation.wav \
    --speaker-diarization
```

Output example:
```
👥 Speakers:
   Speaker_0: 0.0s - 5.2s (duration: 5.2s)
   Speaker_1: 5.2s - 10.4s (duration: 5.2s)
   Speaker_0: 10.4s - 15.0s (duration: 4.6s)
```

### Emotion Detection
```bash
# Detect emotions in speech
python extended_translator.py --mode file --file emotional_speech.wav \
    --emotion-detection
```

Output example:
```
😊 Detected Emotion: Happy (confidence: 0.73)
```

### Custom Vocabulary
```bash
# Improve recognition of technical terms
python extended_translator.py --mode file --file technical_talk.wav \
    --vocabulary "TensorFlow" "PyTorch" "Kubernetes" "API"
```

### Multiple Language Translation
```bash
# Translate to multiple languages simultaneously
python extended_translator.py --mode file --file audio.wav \
    --languages es fr de it pt ru ja zh ko ar
```

Output example:
```
🌍 Translations:
   [ES] Hola, ¿cómo estás?
   [FR] Bonjour, comment allez-vous?
   [DE] Hallo, wie geht es dir?
   [IT] Ciao, come stai?
   ...
```

### Subtitle Export
```bash
# Export as SRT
python extended_translator.py --mode file --file video_audio.wav \
    --export-subtitle srt

# Export as WebVTT
python extended_translator.py --mode file --file video_audio.wav \
    --export-subtitle vtt
```

## API Usage

### Using curl

**Health check:**
```bash
curl http://localhost:8000/health
```

**Transcribe file:**
```bash
curl -X POST "http://localhost:8000/transcribe" \
  -F "file=@audio.wav" \
  -F "target_language=es"
```

**Multiple languages:**
```bash
curl -X POST "http://localhost:8000/transcribe/multiple" \
  -F "file=@audio.wav" \
  -F 'target_languages=["es","fr","de"]'
```

### Using Python

```python
import requests

# Transcribe and translate
with open('audio.wav', 'rb') as f:
    files = {'file': f}
    data = {
        'target_languages': '["es", "fr", "de"]',
        'custom_vocabulary': '["OpenAI", "Whisper"]'
    }
    response = requests.post(
        'http://localhost:8000/transcribe/multiple',
        files=files,
        data=data
    )
    result = response.json()
    
print("Transcription:", result['transcription'])
print("Translations:", result['translations'])
```

### WebSocket Streaming

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/transcribe');

// Send audio data
ws.onopen = () => {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            const mediaRecorder = new MediaRecorder(stream);
            
            mediaRecorder.ondataavailable = (event) => {
                ws.send(event.data);
            };
            
            mediaRecorder.start();
            
            // Stop after 5 seconds
            setTimeout(() => mediaRecorder.stop(), 5000);
        });
};

// Receive results
ws.onmessage = (event) => {
    const result = JSON.parse(event.data);
    console.log('Transcription:', result.transcription);
    console.log('Translations:', result.translations);
};
```

## Programmatic Usage

### Python Module

```python
from extended_translator import ExtendedWhisperTranslator

# Initialize with all features
translator = ExtendedWhisperTranslator(
    model_id="openai/whisper-large-v3",
    target_languages=["es", "fr", "de"],
    enable_audio_enhancement=True,
    enable_speaker_diarization=True,
    enable_emotion_detection=True,
    custom_vocabulary=["OpenAI", "Whisper", "FastAPI"]
)

# Process audio file
import soundfile as sf
audio_data, sr = sf.read("audio.wav")

result = translator.transcribe_with_enhancements(audio_data)

print("Transcription:", result['transcription'])
print("Translations:", result['translations'])
print("Speakers:", result['speakers'])
print("Emotion:", result['emotion'])
```

### Audio Enhancement Only

```python
from audio_enhancement import AudioEnhancer

enhancer = AudioEnhancer(sample_rate=16000)
clean_audio = enhancer.enhance_audio(noisy_audio)
```

### Speaker Diarization Only

```python
from speaker_diarization import SpeakerDiarizer

diarizer = SpeakerDiarizer(sample_rate=16000)
segments = diarizer.diarize(audio_data, n_speakers=2)

for segment in segments:
    print(f"{segment['speaker']}: {segment['start']:.1f}s - {segment['end']:.1f}s")
```

### Emotion Detection Only

```python
from speaker_diarization import EmotionDetector

detector = EmotionDetector(sample_rate=16000)
emotion = detector.detect_emotion(audio_data)

print(f"Emotion: {emotion['emotion']} (confidence: {emotion['confidence']:.2f})")
```

## Configuration

### Command-line Options

```
--mode {realtime,file,web}
                        Operation mode
--file FILE             Audio file path (for file mode)
--languages [LANGUAGES ...]
                        Target languages for translation
--enhance-audio         Enable audio enhancement
--speaker-diarization   Enable speaker diarization
--emotion-detection     Enable emotion detection
--vocabulary [VOCABULARY ...]
                        Custom vocabulary words
--model MODEL           Whisper model ID
--web-port PORT         Port for web API (default: 8000)
--export-subtitle {srt,vtt}
                        Export transcription as subtitle file
```

### Environment Variables

Create a `.env` file:
```env
WHISPER_MODEL_ID=openai/whisper-large-v3
TARGET_LANGUAGE=es
SAMPLE_RATE=16000
CHUNK_DURATION=5.0
WANDB_API_KEY=your_key_here  # Optional
```

## Troubleshooting

### Port already in use
```bash
# Use a different port
python extended_translator.py --mode web --web-port 8080
```

### Out of memory
```bash
# Use a smaller model
python extended_translator.py --mode file --file audio.wav \
    --model "openai/whisper-base"
```

### Audio quality issues
```bash
# Enable audio enhancement
python extended_translator.py --mode file --file audio.wav \
    --enhance-audio
```

### Need faster processing
```bash
# Disable optional features
python extended_translator.py --mode file --file audio.wav \
    --languages es  # Only one language
    # Don't use --speaker-diarization or --emotion-detection
```

## Performance Tips

1. **Use GPU**: Significantly faster transcription
2. **Smaller models**: Use whisper-base or whisper-small for faster processing
3. **Limit languages**: Only translate to languages you need
4. **Disable unused features**: Skip speaker diarization if not needed
5. **Shorter audio chunks**: For real-time, use shorter chunk durations

## Support

- Documentation: See [EXTENDED_FEATURES.md](EXTENDED_FEATURES.md)
- Issues: Open an issue on GitHub
- API Docs: http://localhost:8000/docs (when server is running)

## Next Steps

1. Try the web interface first
2. Experiment with file processing
3. Test real-time recording
4. Integrate into your application via API
5. Customize for your specific use case

Enjoy using the extended Whisper speech recognition system! 🎉
