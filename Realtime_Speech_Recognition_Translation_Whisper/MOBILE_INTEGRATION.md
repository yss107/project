# Mobile App Integration Guide

## Overview

This guide provides comprehensive instructions for integrating the Whisper Real-time Speech Recognition & Translation system with mobile applications on iOS and Android.

## Architecture

```
┌─────────────────┐
│   Mobile App    │
│  (iOS/Android)  │
└────────┬────────┘
         │
         │ REST API / WebSocket
         │
         ▼
┌─────────────────┐
│   Backend API   │
│ (FastAPI Server)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Whisper Model  │
│   Processing    │
└─────────────────┘
```

## Backend API Setup

### 1. Start the Web API

```bash
# Start the server
python web_api.py

# Or use Docker
docker-compose up whisper-api-cpu

# Or deploy to cloud (see DEPLOYMENT.md)
```

The API will be available at `http://localhost:8000` (or your deployment URL).

### 2. API Documentation

Access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## REST API Integration

### Authentication (Optional)

If you implement authentication, add API key to headers:

```
Authorization: Bearer YOUR_API_KEY
```

### Key Endpoints

#### 1. Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "version": "1.0.0"
}
```

#### 2. Transcribe Audio

```http
POST /transcribe
Content-Type: multipart/form-data

file: <audio_file>
target_language: es (optional)
```

**Response:**
```json
{
  "transcription": "Hello, how are you?",
  "translation": "Hola, ¿cómo estás?",
  "language": "en",
  "processing_time": 2.5
}
```

#### 3. Multi-Language Translation

```http
POST /transcribe/multiple
Content-Type: multipart/form-data

file: <audio_file>
languages: ["es", "fr", "de"]
```

**Response:**
```json
{
  "transcription": "Hello, how are you?",
  "translations": {
    "es": "Hola, ¿cómo estás?",
    "fr": "Bonjour, comment allez-vous?",
    "de": "Hallo, wie geht es dir?"
  },
  "processing_time": 3.2
}
```

## WebSocket Integration (Real-time)

### Connection

```javascript
ws://localhost:8000/ws/transcribe
```

### Protocol

1. **Connect** to WebSocket endpoint
2. **Send** audio data as binary chunks
3. **Receive** transcription results in real-time

### Message Format

**Client → Server:**
```
Binary audio data (16-bit PCM, 16kHz, mono)
```

**Server → Client:**
```json
{
  "transcription": "Text spoken",
  "translations": {
    "es": "Texto hablado"
  },
  "timestamp": 1234567890.123,
  "is_final": false
}
```

## iOS Integration

### Using Swift with URLSession

```swift
import Foundation
import AVFoundation

class WhisperClient {
    let baseURL = "http://your-api-url:8000"
    
    // Transcribe audio file
    func transcribe(audioURL: URL, targetLanguage: String = "es", completion: @escaping (Result<TranscriptionResponse, Error>) -> Void) {
        var request = URLRequest(url: URL(string: "\(baseURL)/transcribe")!)
        request.httpMethod = "POST"
        
        let boundary = UUID().uuidString
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        
        var body = Data()
        
        // Add audio file
        if let audioData = try? Data(contentsOf: audioURL) {
            body.append("--\(boundary)\r\n".data(using: .utf8)!)
            body.append("Content-Disposition: form-data; name=\"file\"; filename=\"audio.wav\"\r\n".data(using: .utf8)!)
            body.append("Content-Type: audio/wav\r\n\r\n".data(using: .utf8)!)
            body.append(audioData)
            body.append("\r\n".data(using: .utf8)!)
        }
        
        // Add target language
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"target_language\"\r\n\r\n".data(using: .utf8)!)
        body.append("\(targetLanguage)\r\n".data(using: .utf8)!)
        body.append("--\(boundary)--\r\n".data(using: .utf8)!)
        
        request.httpBody = body
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            
            guard let data = data else {
                completion(.failure(NSError(domain: "WhisperClient", code: -1, userInfo: [NSLocalizedDescriptionKey: "No data received"])))
                return
            }
            
            do {
                let result = try JSONDecoder().decode(TranscriptionResponse.self, from: data)
                completion(.success(result))
            } catch {
                completion(.failure(error))
            }
        }.resume()
    }
    
    // Real-time recording and transcription
    func startRealTimeTranscription() {
        // Connect to WebSocket
        let url = URL(string: "ws://your-api-url:8000/ws/transcribe")!
        let webSocket = URLSession.shared.webSocketTask(with: url)
        
        webSocket.resume()
        
        // Send audio data
        // (See below for audio capture)
        
        // Receive transcriptions
        receiveMessage(webSocket: webSocket)
    }
    
    private func receiveMessage(webSocket: URLSessionWebSocketTask) {
        webSocket.receive { result in
            switch result {
            case .success(let message):
                switch message {
                case .string(let text):
                    print("Received: \(text)")
                    // Parse JSON and update UI
                case .data(let data):
                    print("Received binary data")
                @unknown default:
                    break
                }
                // Continue receiving
                self.receiveMessage(webSocket: webSocket)
            case .failure(let error):
                print("WebSocket error: \(error)")
            }
        }
    }
}

// Response models
struct TranscriptionResponse: Codable {
    let transcription: String
    let translation: String?
    let language: String?
    let processing_time: Double?
}
```

### Audio Recording in iOS

```swift
import AVFoundation

class AudioRecorder: NSObject, AVAudioRecorderDelegate {
    var audioRecorder: AVAudioRecorder?
    
    func startRecording() {
        let audioSession = AVAudioSession.sharedInstance()
        
        do {
            try audioSession.setCategory(.record, mode: .measurement)
            try audioSession.setActive(true)
            
            let settings: [String: Any] = [
                AVFormatIDKey: Int(kAudioFormatLinearPCM),
                AVSampleRateKey: 16000.0,
                AVNumberOfChannelsKey: 1,
                AVLinearPCMBitDepthKey: 16,
                AVLinearPCMIsFloatKey: false,
                AVLinearPCMIsBigEndianKey: false
            ]
            
            let audioURL = getDocumentsDirectory().appendingPathComponent("recording.wav")
            audioRecorder = try AVAudioRecorder(url: audioURL, settings: settings)
            audioRecorder?.delegate = self
            audioRecorder?.record()
            
        } catch {
            print("Failed to start recording: \(error)")
        }
    }
    
    func stopRecording() -> URL? {
        audioRecorder?.stop()
        return audioRecorder?.url
    }
    
    private func getDocumentsDirectory() -> URL {
        FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
    }
}
```

## Android Integration

### Using Kotlin with Retrofit

```kotlin
// API Interface
interface WhisperApi {
    @Multipart
    @POST("transcribe")
    suspend fun transcribe(
        @Part file: MultipartBody.Part,
        @Part("target_language") targetLanguage: RequestBody
    ): TranscriptionResponse
    
    @Multipart
    @POST("transcribe/multiple")
    suspend fun transcribeMultiple(
        @Part file: MultipartBody.Part,
        @Part("languages") languages: RequestBody
    ): MultiTranscriptionResponse
}

// Response models
data class TranscriptionResponse(
    val transcription: String,
    val translation: String?,
    val language: String?,
    val processing_time: Double?
)

data class MultiTranscriptionResponse(
    val transcription: String,
    val translations: Map<String, String>,
    val processing_time: Double?
)

// Client implementation
class WhisperClient(private val baseUrl: String) {
    private val retrofit = Retrofit.Builder()
        .baseUrl(baseUrl)
        .addConverterFactory(GsonConverterFactory.create())
        .build()
    
    private val api = retrofit.create(WhisperApi::class.java)
    
    suspend fun transcribe(audioFile: File, targetLanguage: String = "es"): TranscriptionResponse {
        val requestFile = audioFile.asRequestBody("audio/wav".toMediaTypeOrNull())
        val filePart = MultipartBody.Part.createFormData("file", audioFile.name, requestFile)
        val languagePart = targetLanguage.toRequestBody("text/plain".toMediaTypeOrNull())
        
        return api.transcribe(filePart, languagePart)
    }
    
    suspend fun transcribeMultiple(audioFile: File, languages: List<String>): MultiTranscriptionResponse {
        val requestFile = audioFile.asRequestBody("audio/wav".toMediaTypeOrNull())
        val filePart = MultipartBody.Part.createFormData("file", audioFile.name, requestFile)
        val languagesJson = Gson().toJson(languages)
        val languagesPart = languagesJson.toRequestBody("application/json".toMediaTypeOrNull())
        
        return api.transcribeMultiple(filePart, languagesPart)
    }
}
```

### WebSocket in Android

```kotlin
import okhttp3.*
import okio.ByteString

class WhisperWebSocketClient(private val url: String) {
    private var webSocket: WebSocket? = null
    private val client = OkHttpClient()
    
    fun connect(listener: WebSocketListener) {
        val request = Request.Builder()
            .url(url)
            .build()
        
        webSocket = client.newWebSocket(request, listener)
    }
    
    fun sendAudio(audioData: ByteArray) {
        webSocket?.send(ByteString.of(*audioData))
    }
    
    fun disconnect() {
        webSocket?.close(1000, "Client closing")
    }
}

// Usage
val wsClient = WhisperWebSocketClient("ws://your-api-url:8000/ws/transcribe")

wsClient.connect(object : WebSocketListener() {
    override fun onMessage(webSocket: WebSocket, text: String) {
        // Parse JSON response
        val result = Gson().fromJson(text, TranscriptionResponse::class.java)
        // Update UI
    }
    
    override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
        Log.e("WebSocket", "Error: ${t.message}")
    }
})
```

### Audio Recording in Android

```kotlin
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder

class AudioRecorder {
    private val sampleRate = 16000
    private val channelConfig = AudioFormat.CHANNEL_IN_MONO
    private val audioFormat = AudioFormat.ENCODING_PCM_16BIT
    
    private val bufferSize = AudioRecord.getMinBufferSize(
        sampleRate,
        channelConfig,
        audioFormat
    )
    
    private var audioRecord: AudioRecord? = null
    private var isRecording = false
    
    fun startRecording(onAudioData: (ByteArray) -> Unit) {
        audioRecord = AudioRecord(
            MediaRecorder.AudioSource.MIC,
            sampleRate,
            channelConfig,
            audioFormat,
            bufferSize
        )
        
        audioRecord?.startRecording()
        isRecording = true
        
        Thread {
            val buffer = ByteArray(bufferSize)
            while (isRecording) {
                val read = audioRecord?.read(buffer, 0, bufferSize) ?: 0
                if (read > 0) {
                    onAudioData(buffer.copyOf(read))
                }
            }
        }.start()
    }
    
    fun stopRecording() {
        isRecording = false
        audioRecord?.stop()
        audioRecord?.release()
        audioRecord = null
    }
}
```

## React Native Integration

### Installation

```bash
npm install axios react-native-fs
```

### Implementation

```javascript
import axios from 'axios';
import RNFS from 'react-native-fs';

const API_BASE_URL = 'http://your-api-url:8000';

export class WhisperClient {
  async transcribe(audioPath, targetLanguage = 'es') {
    const formData = new FormData();
    
    // Read audio file
    const audioData = await RNFS.readFile(audioPath, 'base64');
    
    formData.append('file', {
      uri: `file://${audioPath}`,
      type: 'audio/wav',
      name: 'audio.wav'
    });
    
    formData.append('target_language', targetLanguage);
    
    try {
      const response = await axios.post(
        `${API_BASE_URL}/transcribe`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      );
      
      return response.data;
    } catch (error) {
      console.error('Transcription error:', error);
      throw error;
    }
  }
  
  // WebSocket connection
  connectWebSocket(onMessage) {
    const ws = new WebSocket(`ws://${API_BASE_URL}/ws/transcribe`);
    
    ws.onopen = () => {
      console.log('WebSocket connected');
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage(data);
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    return ws;
  }
}
```

## Best Practices

### 1. Audio Format

Always send audio in the following format for best results:
- **Format:** WAV (PCM)
- **Sample Rate:** 16000 Hz
- **Channels:** Mono (1 channel)
- **Bit Depth:** 16-bit

### 2. Error Handling

```javascript
try {
  const result = await client.transcribe(audioFile);
  // Handle success
} catch (error) {
  if (error.response) {
    // Server responded with error
    console.error('Server error:', error.response.status);
  } else if (error.request) {
    // No response received
    console.error('Network error');
  } else {
    // Request setup error
    console.error('Error:', error.message);
  }
}
```

### 3. Timeout Handling

```javascript
const config = {
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'multipart/form-data'
  }
};

const response = await axios.post(url, formData, config);
```

### 4. Offline Support

Implement local caching for offline scenarios:
- Cache recent transcriptions
- Queue requests when offline
- Sync when connection restored

### 5. Performance Optimization

- **Compress audio** before sending (if bandwidth is limited)
- **Batch requests** when processing multiple files
- **Use WebSockets** for real-time streaming
- **Implement retry logic** for failed requests

## Security Considerations

### 1. HTTPS/WSS

Always use HTTPS and WSS in production:

```
https://your-api-url.com
wss://your-api-url.com/ws/transcribe
```

### 2. API Authentication

Implement API key authentication:

```javascript
const headers = {
  'Authorization': 'Bearer YOUR_API_KEY',
  'Content-Type': 'multipart/form-data'
};
```

### 3. Data Privacy

- Never log sensitive audio content
- Implement data retention policies
- Use encryption for stored audio
- Comply with GDPR/privacy regulations

## Testing

### Test Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Transcribe audio file
curl -X POST http://localhost:8000/transcribe \
  -F "file=@test_audio.wav" \
  -F "target_language=es"

# WebSocket test (using wscat)
npm install -g wscat
wscat -c ws://localhost:8000/ws/transcribe
```

## Troubleshooting

### Common Issues

1. **Connection Timeout**
   - Check server is running
   - Verify network connectivity
   - Increase timeout values

2. **Audio Format Error**
   - Ensure audio is in correct format (16kHz, mono, 16-bit PCM)
   - Convert audio before sending

3. **WebSocket Connection Failed**
   - Check firewall settings
   - Verify WebSocket support in network
   - Use WSS for secure connections

4. **Large File Upload Failed**
   - Increase server upload limit
   - Compress audio before sending
   - Split into smaller chunks

## Support

For additional help:
- API Documentation: `http://your-api-url:8000/docs`
- GitHub Issues: [Project Repository]
- Email: support@example.com

---

**Built with ❤️ for mobile developers**
