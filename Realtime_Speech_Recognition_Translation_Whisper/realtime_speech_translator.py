#!/usr/bin/env python3
"""
Real-time Speech Recognition and Translation using OpenAI Whisper Large V3
Integrated with Weights & Biases for LLM-powered application monitoring
"""

import os
import sys
import time
import queue
import warnings
from typing import Optional, List
from datetime import datetime

import numpy as np
import sounddevice as sd
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from deep_translator import GoogleTranslator
import wandb

warnings.filterwarnings('ignore')


class WhisperRealtimeTranslator:
    """Real-time speech recognition and translation using Whisper Large V3"""
    
    def __init__(
        self,
        model_id: str = "openai/whisper-large-v3",
        device: str = "auto",
        target_language: str = "es",  # Spanish by default
        use_wandb: bool = True,
        sample_rate: int = 16000,
        chunk_duration: float = 5.0
    ):
        """
        Initialize the real-time translator
        
        Args:
            model_id: HuggingFace model ID for Whisper
            device: Device to run model on ('cuda', 'cpu', or 'auto')
            target_language: Target language code for translation (e.g., 'es', 'fr', 'de')
            use_wandb: Whether to use Weights & Biases for logging
            sample_rate: Audio sample rate in Hz
            chunk_duration: Duration of audio chunks in seconds
        """
        self.model_id = model_id
        self.target_language = target_language
        self.sample_rate = sample_rate
        self.chunk_duration = chunk_duration
        self.chunk_samples = int(sample_rate * chunk_duration)
        self.use_wandb = use_wandb
        
        # Setup device
        if device == "auto":
            self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        
        self.torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        
        print(f"🚀 Initializing Whisper Large V3 on {self.device}...")
        self._setup_model()
        self._setup_translator()
        
        if self.use_wandb:
            self._setup_wandb()
        
        # Audio queue for real-time processing
        self.audio_queue = queue.Queue()
        self.is_running = False
        
        print("✅ Real-time Speech Recognition & Translation System Ready!")
    
    def _setup_model(self):
        """Setup Whisper model and processor"""
        print("📥 Loading Whisper Large V3 model...")
        
        # Load model
        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
            self.model_id,
            torch_dtype=self.torch_dtype,
            low_cpu_mem_usage=True,
            use_safetensors=True
        )
        self.model.to(self.device)
        
        # Load processor
        self.processor = AutoProcessor.from_pretrained(self.model_id)
        
        # Create pipeline
        self.pipe = pipeline(
            "automatic-speech-recognition",
            model=self.model,
            tokenizer=self.processor.tokenizer,
            feature_extractor=self.processor.feature_extractor,
            max_new_tokens=128,
            chunk_length_s=30,
            batch_size=16,
            return_timestamps=True,
            torch_dtype=self.torch_dtype,
            device=self.device,
        )
        
        print("✅ Whisper model loaded successfully!")
    
    def _setup_translator(self):
        """Setup translation service"""
        try:
            self.translator = GoogleTranslator(target=self.target_language)
            print(f"✅ Translator initialized for target language: {self.target_language}")
        except Exception as e:
            print(f"⚠️ Warning: Could not initialize translator: {e}")
            self.translator = None
    
    def _setup_wandb(self):
        """Setup Weights & Biases for experiment tracking"""
        try:
            wandb.init(
                project="whisper-realtime-translation",
                config={
                    "model": self.model_id,
                    "device": self.device,
                    "target_language": self.target_language,
                    "sample_rate": self.sample_rate,
                    "chunk_duration": self.chunk_duration,
                }
            )
            print("✅ Weights & Biases initialized!")
        except Exception as e:
            print(f"⚠️ Warning: Could not initialize W&B: {e}")
            self.use_wandb = False
    
    def audio_callback(self, indata, frames, time_info, status):
        """Callback for audio stream"""
        if status:
            print(f"⚠️ Audio status: {status}")
        self.audio_queue.put(indata.copy())
    
    def transcribe_audio(self, audio_data: np.ndarray) -> dict:
        """
        Transcribe audio using Whisper
        
        Args:
            audio_data: Audio numpy array
            
        Returns:
            Dictionary with transcription results
        """
        try:
            # Ensure audio is 1D
            if len(audio_data.shape) > 1:
                audio_data = audio_data.mean(axis=1)
            
            # Normalize audio
            audio_data = audio_data.astype(np.float32)
            if np.abs(audio_data).max() > 1.0:
                audio_data = audio_data / np.abs(audio_data).max()
            
            # Transcribe
            result = self.pipe(audio_data, generate_kwargs={"language": "english"})
            return result
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return {"text": "", "chunks": []}
    
    def translate_text(self, text: str) -> Optional[str]:
        """
        Translate text to target language
        
        Args:
            text: Text to translate
            
        Returns:
            Translated text or None if translation fails
        """
        if not text or not self.translator:
            return None
        
        try:
            translated = self.translator.translate(text)
            return translated
        except Exception as e:
            print(f"❌ Translation error: {e}")
            return None
    
    def process_audio_chunk(self, audio_chunk: np.ndarray):
        """Process a single audio chunk"""
        start_time = time.time()
        
        # Transcribe
        result = self.transcribe_audio(audio_chunk)
        transcription = result.get("text", "").strip()
        
        if not transcription:
            return
        
        # Translate
        translation = self.translate_text(transcription)
        
        processing_time = time.time() - start_time
        
        # Display results
        print("\n" + "="*80)
        print(f"🎤 Original ({datetime.now().strftime('%H:%M:%S')}): {transcription}")
        if translation:
            print(f"🌍 Translated ({self.target_language}): {translation}")
        print(f"⏱️  Processing time: {processing_time:.2f}s")
        print("="*80 + "\n")
        
        # Log to W&B
        if self.use_wandb:
            wandb.log({
                "transcription_length": len(transcription),
                "processing_time": processing_time,
                "has_translation": translation is not None,
                "timestamp": time.time()
            })
    
    def start_recording(self, duration: Optional[float] = None):
        """
        Start real-time recording and processing
        
        Args:
            duration: Optional duration in seconds. If None, runs until interrupted
        """
        self.is_running = True
        
        print("\n🎙️  Starting real-time recording...")
        print(f"📊 Sample rate: {self.sample_rate} Hz")
        print(f"⏱️  Chunk duration: {self.chunk_duration}s")
        print(f"🌍 Target language: {self.target_language}")
        print("\n💬 Speak into your microphone...")
        print("⏹️  Press Ctrl+C to stop\n")
        
        try:
            with sd.InputStream(
                channels=1,
                samplerate=self.sample_rate,
                callback=self.audio_callback,
                blocksize=int(self.sample_rate * 0.1)  # 100ms blocks
            ):
                start_time = time.time()
                audio_buffer = []
                
                while self.is_running:
                    # Check duration limit
                    if duration and (time.time() - start_time) > duration:
                        break
                    
                    # Get audio from queue
                    try:
                        chunk = self.audio_queue.get(timeout=0.1)
                        audio_buffer.append(chunk)
                        
                        # Process when buffer reaches chunk duration
                        if len(audio_buffer) * 0.1 >= self.chunk_duration:
                            audio_data = np.concatenate(audio_buffer, axis=0)
                            audio_buffer = []
                            
                            # Process in separate thread to avoid blocking
                            self.process_audio_chunk(audio_data)
                    
                    except queue.Empty:
                        continue
        
        except KeyboardInterrupt:
            print("\n\n⏹️  Recording stopped by user")
        except Exception as e:
            print(f"\n❌ Error during recording: {e}")
        finally:
            self.is_running = False
            if self.use_wandb:
                wandb.finish()
            print("\n✅ Session ended")
    
    def stop_recording(self):
        """Stop recording"""
        self.is_running = False


def main():
    """Main function"""
    print("\n" + "="*80)
    print("🎯 Real-time Speech Recognition & Translation with Whisper Large V3")
    print("="*80 + "\n")
    
    # Configuration
    MODEL_ID = "openai/whisper-large-v3"
    TARGET_LANGUAGE = "es"  # Change to desired language code
    USE_WANDB = False  # Set to True to enable W&B logging (requires API key)
    
    # Check for environment variables
    if os.getenv("WANDB_API_KEY"):
        USE_WANDB = True
    
    # Initialize translator
    translator = WhisperRealtimeTranslator(
        model_id=MODEL_ID,
        target_language=TARGET_LANGUAGE,
        use_wandb=USE_WANDB,
        chunk_duration=5.0
    )
    
    # Start recording
    # Set duration=None for continuous recording, or specify seconds
    translator.start_recording(duration=None)


if __name__ == "__main__":
    main()
