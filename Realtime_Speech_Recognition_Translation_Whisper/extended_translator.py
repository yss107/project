#!/usr/bin/env python3
"""
Extended Real-time Speech Recognition and Translation
Integrates all advanced features: web API, speaker diarization, emotion detection,
audio enhancement, multiple languages, and subtitle export
"""

import os
import sys
import argparse
from typing import List, Optional, Dict, Any
import numpy as np

# Import core translator
from realtime_speech_translator import WhisperRealtimeTranslator

# Import new modules
from audio_enhancement import AudioEnhancer, preprocess_audio_file
from speaker_diarization import SpeakerDiarizer, EmotionDetector, diarize_audio_file


class ExtendedWhisperTranslator(WhisperRealtimeTranslator):
    """
    Extended translator with audio enhancement, speaker diarization,
    emotion detection, and multi-language support
    """
    
    def __init__(
        self,
        model_id: str = "openai/whisper-large-v3",
        device: str = "auto",
        target_languages: List[str] = None,
        use_wandb: bool = False,
        sample_rate: int = 16000,
        chunk_duration: float = 5.0,
        enable_audio_enhancement: bool = True,
        enable_speaker_diarization: bool = False,
        enable_emotion_detection: bool = False,
        custom_vocabulary: Optional[List[str]] = None
    ):
        """
        Initialize extended translator with advanced features
        
        Args:
            model_id: HuggingFace model ID for Whisper
            device: Device to run model on
            target_languages: List of target language codes for translation
            use_wandb: Whether to use Weights & Biases
            sample_rate: Audio sample rate
            chunk_duration: Duration of audio chunks
            enable_audio_enhancement: Enable audio preprocessing
            enable_speaker_diarization: Enable speaker identification
            enable_emotion_detection: Enable emotion detection
            custom_vocabulary: Custom vocabulary for better recognition
        """
        # Initialize base translator
        super().__init__(
            model_id=model_id,
            device=device,
            target_language=target_languages[0] if target_languages else "es",
            use_wandb=use_wandb,
            sample_rate=sample_rate,
            chunk_duration=chunk_duration
        )
        
        # Store additional settings
        self.target_languages = target_languages or ["es"]
        self.custom_vocabulary = custom_vocabulary or []
        
        # Initialize enhancement modules
        self.enable_audio_enhancement = enable_audio_enhancement
        if enable_audio_enhancement:
            self.audio_enhancer = AudioEnhancer(sample_rate=sample_rate)
            print("✅ Audio enhancement enabled")
        
        # Initialize speaker diarization
        self.enable_speaker_diarization = enable_speaker_diarization
        if enable_speaker_diarization:
            self.speaker_diarizer = SpeakerDiarizer(sample_rate=sample_rate)
            print("✅ Speaker diarization enabled")
        
        # Initialize emotion detection
        self.enable_emotion_detection = enable_emotion_detection
        if enable_emotion_detection:
            self.emotion_detector = EmotionDetector(sample_rate=sample_rate)
            print("✅ Emotion detection enabled")
    
    def enhance_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply audio enhancement if enabled"""
        if self.enable_audio_enhancement and hasattr(self, 'audio_enhancer'):
            return self.audio_enhancer.enhance_audio(audio_data)
        return audio_data
    
    def apply_custom_vocabulary(self, text: str) -> str:
        """Apply custom vocabulary replacements"""
        if not self.custom_vocabulary:
            return text
        
        result = text
        for word in self.custom_vocabulary:
            # Case-insensitive replacement preserving original case pattern
            import re
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            result = pattern.sub(word, result)
        
        return result
    
    def transcribe_with_enhancements(
        self,
        audio_data: np.ndarray
    ) -> Dict[str, Any]:
        """
        Transcribe audio with all enhancements
        
        Args:
            audio_data: Input audio array
            
        Returns:
            Dictionary with enhanced transcription results
        """
        import time
        start_time = time.time()
        
        # Enhance audio
        if self.enable_audio_enhancement:
            audio_data = self.enhance_audio(audio_data)
        
        # Transcribe
        result = self.transcribe_audio(audio_data)
        transcription = result.get("text", "").strip()
        
        # Apply custom vocabulary
        if transcription and self.custom_vocabulary:
            transcription = self.apply_custom_vocabulary(transcription)
        
        # Translate to multiple languages
        translations = {}
        if transcription:
            for lang in self.target_languages:
                # Temporarily change target language
                original_target = self.target_language
                self.target_language = lang
                self._setup_translator()
                
                translation = self.translate_text(transcription)
                if translation:
                    translations[lang] = translation
                
                # Restore original target
                self.target_language = original_target
                self._setup_translator()
        
        # Speaker diarization
        speakers = []
        if self.enable_speaker_diarization and hasattr(self, 'speaker_diarizer'):
            try:
                speakers = self.speaker_diarizer.diarize(audio_data)
            except Exception as e:
                print(f"⚠️ Speaker diarization failed: {e}")
        
        # Emotion detection
        emotion = None
        if self.enable_emotion_detection and hasattr(self, 'emotion_detector'):
            try:
                emotion = self.emotion_detector.detect_emotion(audio_data)
            except Exception as e:
                print(f"⚠️ Emotion detection failed: {e}")
        
        processing_time = time.time() - start_time
        
        # Compile results
        enhanced_result = {
            "transcription": transcription,
            "translations": translations,
            "processing_time": processing_time,
            "chunks": result.get("chunks", []),
            "speakers": speakers if speakers else None,
            "emotion": emotion,
            "enhancements_applied": {
                "audio_enhancement": self.enable_audio_enhancement,
                "speaker_diarization": self.enable_speaker_diarization,
                "emotion_detection": self.enable_emotion_detection,
                "custom_vocabulary": len(self.custom_vocabulary) > 0
            }
        }
        
        return enhanced_result
    
    def process_audio_chunk_enhanced(self, audio_chunk: np.ndarray):
        """Process audio chunk with all enhancements and display results"""
        from datetime import datetime
        
        result = self.transcribe_with_enhancements(audio_chunk)
        
        if not result["transcription"]:
            return
        
        # Display results
        print("\n" + "=" * 80)
        print(f"🎤 Transcription ({datetime.now().strftime('%H:%M:%S')}):")
        print(f"   {result['transcription']}")
        
        # Show translations
        if result["translations"]:
            print("\n🌍 Translations:")
            for lang, translation in result["translations"].items():
                print(f"   [{lang.upper()}] {translation}")
        
        # Show speaker information
        if result["speakers"]:
            print("\n👥 Speakers:")
            for speaker in result["speakers"][:3]:  # Show first 3 segments
                print(f"   {speaker['speaker']}: {speaker['start']:.1f}s - {speaker['end']:.1f}s")
        
        # Show emotion
        if result["emotion"]:
            emotion_info = result["emotion"]
            print(f"\n😊 Emotion: {emotion_info['emotion'].capitalize()} "
                  f"(confidence: {emotion_info['confidence']:.2f})")
        
        # Show processing info
        print(f"\n⏱️  Processing time: {result['processing_time']:.2f}s")
        print("=" * 80 + "\n")
        
        return result


def main():
    """Main function with command-line interface"""
    parser = argparse.ArgumentParser(
        description="Extended Whisper Real-time Speech Recognition & Translation"
    )
    
    parser.add_argument(
        "--mode",
        type=str,
        choices=["realtime", "file", "web"],
        default="realtime",
        help="Operation mode: realtime (microphone), file (process audio file), or web (start web API)"
    )
    
    parser.add_argument(
        "--file",
        type=str,
        help="Audio file path (for file mode)"
    )
    
    parser.add_argument(
        "--languages",
        type=str,
        nargs="+",
        default=["es"],
        help="Target languages for translation (e.g., es fr de)"
    )
    
    parser.add_argument(
        "--enhance-audio",
        action="store_true",
        default=True,
        help="Enable audio enhancement"
    )
    
    parser.add_argument(
        "--speaker-diarization",
        action="store_true",
        help="Enable speaker diarization"
    )
    
    parser.add_argument(
        "--emotion-detection",
        action="store_true",
        help="Enable emotion detection"
    )
    
    parser.add_argument(
        "--vocabulary",
        type=str,
        nargs="+",
        help="Custom vocabulary words"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        default="openai/whisper-large-v3",
        help="Whisper model ID"
    )
    
    parser.add_argument(
        "--web-port",
        type=int,
        default=8000,
        help="Port for web API (web mode only)"
    )
    
    parser.add_argument(
        "--export-subtitle",
        type=str,
        choices=["srt", "vtt"],
        help="Export transcription as subtitle file"
    )
    
    args = parser.parse_args()
    
    print("\n" + "=" * 80)
    print("🎯 Extended Whisper Speech Recognition & Translation")
    print("=" * 80 + "\n")
    
    # Web API mode
    if args.mode == "web":
        from web_api import run_server
        print("🌐 Starting Web API server...")
        print(f"📍 Access the web interface at: http://localhost:{args.web_port}")
        print(f"📚 API documentation at: http://localhost:{args.web_port}/docs")
        run_server(port=args.web_port)
        return
    
    # Initialize translator with enhancements
    translator = ExtendedWhisperTranslator(
        model_id=args.model,
        target_languages=args.languages,
        use_wandb=False,
        enable_audio_enhancement=args.enhance_audio,
        enable_speaker_diarization=args.speaker_diarization,
        enable_emotion_detection=args.emotion_detection,
        custom_vocabulary=args.vocabulary
    )
    
    print(f"🎯 Mode: {args.mode}")
    print(f"🌍 Target languages: {', '.join(args.languages)}")
    
    if args.vocabulary:
        print(f"📝 Custom vocabulary: {', '.join(args.vocabulary)}")
    
    print()
    
    # File processing mode
    if args.mode == "file":
        if not args.file:
            print("❌ Error: --file argument required for file mode")
            return
        
        if not os.path.exists(args.file):
            print(f"❌ Error: File not found: {args.file}")
            return
        
        print(f"📁 Processing file: {args.file}")
        
        # Load and enhance audio
        audio_data, sr = preprocess_audio_file(
            args.file,
            sample_rate=translator.sample_rate,
            enhance=args.enhance_audio
        )
        
        # Process
        result = translator.transcribe_with_enhancements(audio_data)
        
        # Display results
        print("\n" + "=" * 80)
        print("TRANSCRIPTION RESULTS")
        print("=" * 80)
        
        print(f"\n📝 Original Text:")
        print(f"   {result['transcription']}")
        
        if result["translations"]:
            print(f"\n🌍 Translations:")
            for lang, translation in result["translations"].items():
                print(f"   [{lang.upper()}] {translation}")
        
        if result["speakers"]:
            print(f"\n👥 Speaker Segments:")
            for speaker in result["speakers"]:
                print(f"   {speaker['speaker']}: {speaker['start']:.1f}s - {speaker['end']:.1f}s "
                      f"(duration: {speaker['duration']:.1f}s)")
        
        if result["emotion"]:
            emotion_info = result["emotion"]
            print(f"\n😊 Detected Emotion: {emotion_info['emotion'].capitalize()} "
                  f"(confidence: {emotion_info['confidence']:.2f})")
        
        print(f"\n⏱️  Processing Time: {result['processing_time']:.2f}s")
        print("=" * 80 + "\n")
        
        # Export subtitle if requested
        if args.export_subtitle:
            from web_api import generate_srt_subtitle, generate_vtt_subtitle
            
            output_file = args.file.rsplit('.', 1)[0] + f".{args.export_subtitle}"
            
            if args.export_subtitle == "srt":
                subtitle_content = generate_srt_subtitle(result, result['transcription'])
            else:
                subtitle_content = generate_vtt_subtitle(result, result['transcription'])
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(subtitle_content)
            
            print(f"💾 Subtitle exported: {output_file}\n")
    
    # Real-time mode
    else:
        print("🎙️  Real-time recording mode")
        print("💬 Speak into your microphone...")
        print("⏹️  Press Ctrl+C to stop\n")
        
        # Override process method to use enhanced version
        translator.process_audio_chunk = translator.process_audio_chunk_enhanced
        
        # Start recording
        translator.start_recording(duration=None)


if __name__ == "__main__":
    main()
