#!/usr/bin/env python3
"""
FastAPI Web Interface for Real-time Speech Recognition & Translation
Supports REST API, WebSocket streaming, and web UI
"""

import os
import io
import json
import asyncio
import tempfile
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path

import numpy as np
import soundfile as sf
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from realtime_speech_translator import WhisperRealtimeTranslator


# ============================================================================
# Pydantic Models
# ============================================================================

class TranscriptionRequest(BaseModel):
    """Request model for transcription"""
    target_languages: List[str] = Field(default=["es"], description="Target languages for translation")
    include_timestamps: bool = Field(default=True, description="Include timestamps in response")
    custom_vocabulary: Optional[List[str]] = Field(default=None, description="Custom vocabulary words")


class TranscriptionResponse(BaseModel):
    """Response model for transcription"""
    transcription: str
    translations: Dict[str, str]
    processing_time: float
    timestamp: str
    chunks: Optional[List[Dict[str, Any]]] = None


class SubtitleRequest(BaseModel):
    """Request model for subtitle generation"""
    format: str = Field(default="srt", description="Subtitle format: srt or vtt")
    target_language: Optional[str] = Field(default=None, description="Language for translation")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    model_loaded: bool
    device: str
    timestamp: str


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="Whisper Real-time Speech Recognition & Translation API",
    description="REST API and WebSocket interface for speech recognition and translation",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global translator instance
translator: Optional[WhisperRealtimeTranslator] = None


# ============================================================================
# Helper Functions
# ============================================================================

def generate_srt_subtitle(transcription_data: Dict[str, Any], text: Optional[str] = None) -> str:
    """Generate SRT format subtitle"""
    srt_content = []
    chunks = transcription_data.get("chunks", [])
    
    if not chunks and text:
        # Simple case: no chunks, just full text
        srt_content.append("1")
        srt_content.append("00:00:00,000 --> 00:00:05,000")
        srt_content.append(text)
        srt_content.append("")
    else:
        # Use chunks with timestamps
        for i, chunk in enumerate(chunks, 1):
            timestamp_start = chunk.get("timestamp", [0, 0])[0]
            timestamp_end = chunk.get("timestamp", [0, 0])[1]
            text_chunk = chunk.get("text", "").strip()
            
            if not text_chunk:
                continue
            
            # Convert seconds to SRT time format
            start_time = format_srt_time(timestamp_start)
            end_time = format_srt_time(timestamp_end)
            
            srt_content.append(str(i))
            srt_content.append(f"{start_time} --> {end_time}")
            srt_content.append(text_chunk)
            srt_content.append("")
    
    return "\n".join(srt_content)


def generate_vtt_subtitle(transcription_data: Dict[str, Any], text: Optional[str] = None) -> str:
    """Generate WebVTT format subtitle"""
    vtt_content = ["WEBVTT", ""]
    chunks = transcription_data.get("chunks", [])
    
    if not chunks and text:
        # Simple case: no chunks, just full text
        vtt_content.append("00:00:00.000 --> 00:00:05.000")
        vtt_content.append(text)
        vtt_content.append("")
    else:
        # Use chunks with timestamps
        for chunk in chunks:
            timestamp_start = chunk.get("timestamp", [0, 0])[0]
            timestamp_end = chunk.get("timestamp", [0, 0])[1]
            text_chunk = chunk.get("text", "").strip()
            
            if not text_chunk:
                continue
            
            # Convert seconds to VTT time format
            start_time = format_vtt_time(timestamp_start)
            end_time = format_vtt_time(timestamp_end)
            
            vtt_content.append(f"{start_time} --> {end_time}")
            vtt_content.append(text_chunk)
            vtt_content.append("")
    
    return "\n".join(vtt_content)


def format_srt_time(seconds: float) -> str:
    """Format time in SRT format: HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def format_vtt_time(seconds: float) -> str:
    """Format time in WebVTT format: HH:MM:SS.mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


async def process_audio_with_multiple_languages(
    audio_data: np.ndarray,
    target_languages: List[str],
    custom_vocabulary: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Process audio and translate to multiple languages"""
    import time
    start_time = time.time()
    
    # Transcribe
    result = translator.transcribe_audio(audio_data)
    transcription = result.get("text", "").strip()
    
    if not transcription:
        return {
            "transcription": "",
            "translations": {},
            "processing_time": time.time() - start_time,
            "timestamp": datetime.now().isoformat(),
            "chunks": result.get("chunks", [])
        }
    
    # Apply custom vocabulary if provided
    if custom_vocabulary:
        transcription = apply_custom_vocabulary(transcription, custom_vocabulary)
    
    # Translate to multiple languages
    translations = {}
    for lang in target_languages:
        # Temporarily change translator target language
        original_target = translator.target_language
        translator.target_language = lang
        translator._setup_translator()
        
        translation = translator.translate_text(transcription)
        if translation:
            translations[lang] = translation
        
        translator.target_language = original_target
        translator._setup_translator()
    
    processing_time = time.time() - start_time
    
    return {
        "transcription": transcription,
        "translations": translations,
        "processing_time": processing_time,
        "timestamp": datetime.now().isoformat(),
        "chunks": result.get("chunks", [])
    }


def apply_custom_vocabulary(text: str, vocabulary: List[str]) -> str:
    """Apply custom vocabulary replacements (simple implementation)"""
    # This is a basic implementation - can be enhanced with fuzzy matching
    result = text
    for word in vocabulary:
        # Simple case-insensitive replacement
        result = result.replace(word.lower(), word)
        result = result.replace(word.upper(), word)
        result = result.replace(word.title(), word)
    return result


# ============================================================================
# API Endpoints
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize the translator on startup"""
    global translator
    print("🚀 Initializing Whisper model...")
    translator = WhisperRealtimeTranslator(
        model_id=os.getenv("WHISPER_MODEL_ID", "openai/whisper-large-v3"),
        target_language=os.getenv("TARGET_LANGUAGE", "es"),
        use_wandb=False,  # Disable W&B for web API
        chunk_duration=5.0
    )
    print("✅ API ready!")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main web interface"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Whisper Real-time Speech Translation</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                border-bottom: 3px solid #007bff;
                padding-bottom: 10px;
            }
            .section {
                margin: 30px 0;
            }
            .button {
                background: #007bff;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                margin: 5px;
            }
            .button:hover {
                background: #0056b3;
            }
            .button:disabled {
                background: #ccc;
                cursor: not-allowed;
            }
            .output {
                background: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                margin: 10px 0;
                min-height: 100px;
                border-left: 4px solid #007bff;
            }
            .transcription {
                font-size: 18px;
                color: #333;
                margin: 10px 0;
            }
            .translation {
                font-size: 16px;
                color: #666;
                margin: 10px 0;
                padding-left: 20px;
            }
            input[type="file"] {
                padding: 10px;
                margin: 10px 0;
            }
            select, input[type="text"] {
                padding: 10px;
                margin: 5px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
            }
            .status {
                padding: 10px;
                border-radius: 5px;
                margin: 10px 0;
            }
            .status.connected {
                background: #d4edda;
                color: #155724;
            }
            .status.disconnected {
                background: #f8d7da;
                color: #721c24;
            }
            .language-select {
                margin: 10px 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎤 Whisper Real-time Speech Recognition & Translation</h1>
            
            <div class="section">
                <h2>📝 Upload Audio File</h2>
                <input type="file" id="audioFile" accept="audio/*">
                <div class="language-select">
                    <label>Target Languages:</label>
                    <select id="languages" multiple>
                        <option value="es" selected>Spanish</option>
                        <option value="fr">French</option>
                        <option value="de">German</option>
                        <option value="it">Italian</option>
                        <option value="pt">Portuguese</option>
                        <option value="ru">Russian</option>
                        <option value="ja">Japanese</option>
                        <option value="zh">Chinese</option>
                        <option value="ko">Korean</option>
                        <option value="ar">Arabic</option>
                    </select>
                </div>
                <button class="button" onclick="uploadAudio()">Transcribe & Translate</button>
                <button class="button" onclick="exportSubtitles('srt')">Export SRT</button>
                <button class="button" onclick="exportSubtitles('vtt')">Export VTT</button>
                
                <div id="fileOutput" class="output">
                    <div class="transcription">Transcription will appear here...</div>
                </div>
            </div>
            
            <div class="section">
                <h2>🎙️ Real-time WebSocket Streaming</h2>
                <div id="wsStatus" class="status disconnected">WebSocket: Disconnected</div>
                <button class="button" id="wsConnect" onclick="toggleWebSocket()">Connect WebSocket</button>
                <button class="button" id="wsStartRecord" onclick="startRecording()" disabled>Start Recording</button>
                <button class="button" id="wsStopRecord" onclick="stopRecording()" disabled>Stop Recording</button>
                
                <div id="wsOutput" class="output">
                    <div class="transcription">Real-time transcription will appear here...</div>
                </div>
            </div>
            
            <div class="section">
                <h2>ℹ️ API Documentation</h2>
                <p>Available endpoints:</p>
                <ul>
                    <li><code>GET /health</code> - Health check</li>
                    <li><code>POST /transcribe</code> - Transcribe audio file</li>
                    <li><code>POST /transcribe/multiple</code> - Transcribe with multiple languages</li>
                    <li><code>POST /export/subtitle</code> - Export subtitles (SRT/VTT)</li>
                    <li><code>WS /ws/transcribe</code> - WebSocket for real-time streaming</li>
                    <li><code>GET /docs</code> - Interactive API documentation</li>
                </ul>
            </div>
        </div>
        
        <script>
            let ws = null;
            let mediaRecorder = null;
            let audioChunks = [];
            let lastTranscription = null;
            
            function toggleWebSocket() {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    ws.close();
                } else {
                    connectWebSocket();
                }
            }
            
            function connectWebSocket() {
                const wsUrl = `ws://${window.location.host}/ws/transcribe`;
                ws = new WebSocket(wsUrl);
                
                ws.onopen = () => {
                    document.getElementById('wsStatus').className = 'status connected';
                    document.getElementById('wsStatus').textContent = 'WebSocket: Connected';
                    document.getElementById('wsConnect').textContent = 'Disconnect WebSocket';
                    document.getElementById('wsStartRecord').disabled = false;
                };
                
                ws.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    displayWebSocketResult(data);
                };
                
                ws.onclose = () => {
                    document.getElementById('wsStatus').className = 'status disconnected';
                    document.getElementById('wsStatus').textContent = 'WebSocket: Disconnected';
                    document.getElementById('wsConnect').textContent = 'Connect WebSocket';
                    document.getElementById('wsStartRecord').disabled = true;
                    document.getElementById('wsStopRecord').disabled = true;
                };
                
                ws.onerror = (error) => {
                    console.error('WebSocket error:', error);
                };
            }
            
            async function startRecording() {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    mediaRecorder = new MediaRecorder(stream);
                    audioChunks = [];
                    
                    mediaRecorder.ondataavailable = (event) => {
                        audioChunks.push(event.data);
                    };
                    
                    mediaRecorder.onstop = async () => {
                        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                        const reader = new FileReader();
                        reader.onloadend = () => {
                            if (ws && ws.readyState === WebSocket.OPEN) {
                                ws.send(reader.result);
                            }
                        };
                        reader.readAsArrayBuffer(audioBlob);
                    };
                    
                    mediaRecorder.start();
                    document.getElementById('wsStartRecord').disabled = true;
                    document.getElementById('wsStopRecord').disabled = false;
                    
                    // Auto-stop after 5 seconds
                    setTimeout(() => {
                        if (mediaRecorder && mediaRecorder.state === 'recording') {
                            stopRecording();
                        }
                    }, 5000);
                    
                } catch (error) {
                    console.error('Error accessing microphone:', error);
                    alert('Error accessing microphone. Please check permissions.');
                }
            }
            
            function stopRecording() {
                if (mediaRecorder && mediaRecorder.state === 'recording') {
                    mediaRecorder.stop();
                    document.getElementById('wsStartRecord').disabled = false;
                    document.getElementById('wsStopRecord').disabled = true;
                }
            }
            
            function displayWebSocketResult(data) {
                const output = document.getElementById('wsOutput');
                let html = `<div class="transcription">🎤 ${data.transcription}</div>`;
                
                if (data.translations) {
                    for (const [lang, translation] of Object.entries(data.translations)) {
                        html += `<div class="translation">🌍 ${lang.toUpperCase()}: ${translation}</div>`;
                    }
                }
                
                html += `<div style="color: #999; font-size: 12px; margin-top: 10px;">
                    Processing time: ${data.processing_time.toFixed(2)}s | ${data.timestamp}
                </div>`;
                
                output.innerHTML = html;
                lastTranscription = data;
            }
            
            async function uploadAudio() {
                const fileInput = document.getElementById('audioFile');
                const file = fileInput.files[0];
                
                if (!file) {
                    alert('Please select an audio file');
                    return;
                }
                
                const formData = new FormData();
                formData.append('file', file);
                
                const languageSelect = document.getElementById('languages');
                const selectedLanguages = Array.from(languageSelect.selectedOptions).map(opt => opt.value);
                formData.append('target_languages', JSON.stringify(selectedLanguages));
                
                try {
                    const response = await fetch('/transcribe/multiple', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const data = await response.json();
                    displayFileResult(data);
                    lastTranscription = data;
                } catch (error) {
                    console.error('Error uploading file:', error);
                    alert('Error processing file');
                }
            }
            
            function displayFileResult(data) {
                const output = document.getElementById('fileOutput');
                let html = `<div class="transcription">📝 ${data.transcription}</div>`;
                
                if (data.translations) {
                    for (const [lang, translation] of Object.entries(data.translations)) {
                        html += `<div class="translation">🌍 ${lang.toUpperCase()}: ${translation}</div>`;
                    }
                }
                
                html += `<div style="color: #999; font-size: 12px; margin-top: 10px;">
                    Processing time: ${data.processing_time.toFixed(2)}s | ${data.timestamp}
                </div>`;
                
                output.innerHTML = html;
            }
            
            async function exportSubtitles(format) {
                if (!lastTranscription) {
                    alert('Please transcribe audio first');
                    return;
                }
                
                try {
                    const response = await fetch('/export/subtitle', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            transcription_data: lastTranscription,
                            format: format
                        })
                    });
                    
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `subtitles.${format}`;
                    a.click();
                    window.URL.revokeObjectURL(url);
                } catch (error) {
                    console.error('Error exporting subtitles:', error);
                    alert('Error exporting subtitles');
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy" if translator else "initializing",
        model_loaded=translator is not None,
        device=translator.device if translator else "unknown",
        timestamp=datetime.now().isoformat()
    )


@app.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    file: UploadFile = File(...),
    target_language: str = Form(default="es")
):
    """Transcribe audio file and translate to target language"""
    if not translator:
        raise HTTPException(status_code=503, detail="Model not loaded yet")
    
    try:
        # Read audio file
        audio_bytes = await file.read()
        audio_data, sample_rate = sf.read(io.BytesIO(audio_bytes))
        
        # Resample if necessary
        if sample_rate != translator.sample_rate:
            import scipy.signal as signal
            num_samples = int(len(audio_data) * translator.sample_rate / sample_rate)
            audio_data = signal.resample(audio_data, num_samples)
        
        # Process audio
        result = await process_audio_with_multiple_languages(
            audio_data,
            [target_language]
        )
        
        return TranscriptionResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/transcribe/multiple", response_model=TranscriptionResponse)
async def transcribe_audio_multiple_languages(
    file: UploadFile = File(...),
    target_languages: str = Form(default='["es"]'),
    custom_vocabulary: Optional[str] = Form(default=None)
):
    """Transcribe audio file and translate to multiple languages"""
    if not translator:
        raise HTTPException(status_code=503, detail="Model not loaded yet")
    
    try:
        # Parse target languages
        target_langs = json.loads(target_languages)
        
        # Parse custom vocabulary
        vocab = json.loads(custom_vocabulary) if custom_vocabulary else None
        
        # Read audio file
        audio_bytes = await file.read()
        audio_data, sample_rate = sf.read(io.BytesIO(audio_bytes))
        
        # Resample if necessary
        if sample_rate != translator.sample_rate:
            import scipy.signal as signal
            num_samples = int(len(audio_data) * translator.sample_rate / sample_rate)
            audio_data = signal.resample(audio_data, num_samples)
        
        # Process audio
        result = await process_audio_with_multiple_languages(
            audio_data,
            target_langs,
            vocab
        )
        
        return TranscriptionResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/export/subtitle")
async def export_subtitle(
    transcription_data: Dict[str, Any],
    format: str = "srt",
    target_language: Optional[str] = None
):
    """Export transcription as subtitle file (SRT or VTT)"""
    try:
        # Get text to export
        if target_language and target_language in transcription_data.get("translations", {}):
            text = transcription_data["translations"][target_language]
        else:
            text = transcription_data.get("transcription", "")
        
        # Generate subtitle
        if format.lower() == "srt":
            subtitle_content = generate_srt_subtitle(transcription_data, text)
            media_type = "application/x-subrip"
        elif format.lower() == "vtt":
            subtitle_content = generate_vtt_subtitle(transcription_data, text)
            media_type = "text/vtt"
        else:
            raise HTTPException(status_code=400, detail="Invalid format. Use 'srt' or 'vtt'")
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{format}', delete=False) as f:
            f.write(subtitle_content)
            temp_path = f.name
        
        return FileResponse(
            temp_path,
            media_type=media_type,
            filename=f"subtitles.{format}"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/transcribe")
async def websocket_transcribe(websocket: WebSocket):
    """WebSocket endpoint for real-time transcription streaming"""
    await websocket.accept()
    
    try:
        while True:
            # Receive audio data
            data = await websocket.receive_bytes()
            
            # Convert bytes to audio
            audio_data, sample_rate = sf.read(io.BytesIO(data))
            
            # Resample if necessary
            if sample_rate != translator.sample_rate:
                import scipy.signal as signal
                num_samples = int(len(audio_data) * translator.sample_rate / sample_rate)
                audio_data = signal.resample(audio_data, num_samples)
            
            # Process audio
            result = await process_audio_with_multiple_languages(
                audio_data,
                ["es", "fr"]  # Default to Spanish and French
            )
            
            # Send result back
            await websocket.send_json(result)
    
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close()


# ============================================================================
# Main
# ============================================================================

def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the FastAPI server"""
    print(f"\n{'='*80}")
    print(f"🌐 Starting Whisper Web API Server")
    print(f"{'='*80}\n")
    print(f"📍 Server: http://{host}:{port}")
    print(f"📚 API Docs: http://{host}:{port}/docs")
    print(f"🎤 Web UI: http://{host}:{port}")
    print(f"\n{'='*80}\n")
    
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()
