#!/usr/bin/env python3
"""
Advanced Speaker Identification with Pyannote.audio
Uses pre-trained models for real-time speaker identification and diarization
"""

import numpy as np
import torch
from typing import List, Dict, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')


class AdvancedSpeakerIdentifier:
    """
    Advanced speaker identification using pyannote.audio pre-trained models
    Provides state-of-the-art speaker diarization and identification
    """
    
    def __init__(
        self,
        device: str = "auto",
        hf_token: Optional[str] = None,
        min_speakers: int = 1,
        max_speakers: int = 10
    ):
        """
        Initialize advanced speaker identifier
        
        Args:
            device: Device to run model on ('cuda', 'cpu', or 'auto')
            hf_token: HuggingFace token for model access
            min_speakers: Minimum number of speakers
            max_speakers: Maximum number of speakers
        """
        # Determine device
        if device == "auto":
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
        
        print(f"🔧 Initializing speaker identifier on {self.device}")
        
        self.hf_token = hf_token or self._get_hf_token()
        self.min_speakers = min_speakers
        self.max_speakers = max_speakers
        
        # Initialize models
        self._initialize_models()
    
    def _get_hf_token(self) -> Optional[str]:
        """Get HuggingFace token from environment"""
        import os
        return os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    
    def _initialize_models(self):
        """Initialize pyannote.audio models"""
        try:
            from pyannote.audio import Pipeline
            
            # Load speaker diarization pipeline
            print("📥 Loading pyannote speaker diarization model...")
            self.diarization_pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=self.hf_token
            )
            
            if self.device.type == "cuda":
                self.diarization_pipeline.to(self.device)
            
            # Load speaker embedding model for identification
            print("📥 Loading speaker embedding model...")
            from pyannote.audio import Model
            self.embedding_model = Model.from_pretrained(
                "pyannote/embedding",
                use_auth_token=self.hf_token
            )
            
            if self.device.type == "cuda":
                self.embedding_model.to(self.device)
            
            print("✅ Speaker identification models loaded successfully")
            
        except ImportError as e:
            print(f"⚠️ Warning: pyannote.audio not available: {e}")
            print("   Install with: pip install pyannote.audio")
            self.diarization_pipeline = None
            self.embedding_model = None
        except Exception as e:
            print(f"⚠️ Warning: Could not initialize speaker models: {e}")
            print("   You may need to accept user agreement at:")
            print("   https://huggingface.co/pyannote/speaker-diarization-3.1")
            print("   https://huggingface.co/pyannote/embedding")
            self.diarization_pipeline = None
            self.embedding_model = None
    
    def diarize_audio(
        self,
        audio_path: str,
        min_speakers: Optional[int] = None,
        max_speakers: Optional[int] = None
    ) -> List[Dict]:
        """
        Perform speaker diarization on audio file
        
        Args:
            audio_path: Path to audio file
            min_speakers: Override minimum number of speakers
            max_speakers: Override maximum number of speakers
            
        Returns:
            List of speaker segments with timestamps
        """
        if self.diarization_pipeline is None:
            raise RuntimeError("Speaker diarization model not initialized")
        
        min_spk = min_speakers if min_speakers is not None else self.min_speakers
        max_spk = max_speakers if max_speakers is not None else self.max_speakers
        
        print(f"🎯 Running speaker diarization on {audio_path}...")
        
        # Run diarization
        diarization = self.diarization_pipeline(
            audio_path,
            min_speakers=min_spk,
            max_speakers=max_spk
        )
        
        # Convert to list of segments
        segments = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segments.append({
                "speaker": speaker,
                "start": turn.start,
                "end": turn.end,
                "duration": turn.end - turn.start
            })
        
        print(f"✅ Found {len(set(s['speaker'] for s in segments))} speakers")
        print(f"   Total segments: {len(segments)}")
        
        return segments
    
    def extract_speaker_embeddings(
        self,
        audio_path: str,
        segments: List[Dict]
    ) -> Dict[str, np.ndarray]:
        """
        Extract speaker embeddings for each speaker
        
        Args:
            audio_path: Path to audio file
            segments: List of speaker segments from diarization
            
        Returns:
            Dictionary mapping speaker labels to embeddings
        """
        if self.embedding_model is None:
            raise RuntimeError("Speaker embedding model not initialized")
        
        from pyannote.audio import Inference
        inference = Inference(self.embedding_model, window="whole")
        
        speaker_embeddings = {}
        
        for segment in segments:
            speaker = segment["speaker"]
            if speaker not in speaker_embeddings:
                # Extract embedding for this speaker's segment
                from pyannote.core import Segment
                seg = Segment(segment["start"], segment["end"])
                embedding = inference.crop(audio_path, seg)
                speaker_embeddings[speaker] = embedding
        
        return speaker_embeddings
    
    def identify_speaker(
        self,
        audio_segment: np.ndarray,
        known_speakers: Dict[str, np.ndarray],
        sample_rate: int = 16000,
        threshold: float = 0.7
    ) -> Tuple[Optional[str], float]:
        """
        Identify speaker from audio segment against known speakers
        
        Args:
            audio_segment: Audio array
            known_speakers: Dictionary of known speaker embeddings
            sample_rate: Audio sample rate
            threshold: Similarity threshold for identification
            
        Returns:
            Tuple of (speaker_label, confidence_score)
        """
        if self.embedding_model is None:
            raise RuntimeError("Speaker embedding model not initialized")
        
        # Save audio segment to temporary file
        import tempfile
        import soundfile as sf
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            sf.write(tmp.name, audio_segment, sample_rate)
            tmp_path = tmp.name
        
        try:
            # Extract embedding
            from pyannote.audio import Inference
            inference = Inference(self.embedding_model, window="whole")
            test_embedding = inference(tmp_path)
            
            # Compare with known speakers
            best_match = None
            best_score = 0.0
            
            for speaker_name, speaker_embedding in known_speakers.items():
                # Calculate cosine similarity
                similarity = np.dot(test_embedding, speaker_embedding) / (
                    np.linalg.norm(test_embedding) * np.linalg.norm(speaker_embedding)
                )
                
                if similarity > best_score:
                    best_score = similarity
                    best_match = speaker_name
            
            # Return match if above threshold
            if best_score >= threshold:
                return best_match, best_score
            else:
                return None, best_score
                
        finally:
            # Clean up temporary file
            import os
            try:
                os.unlink(tmp_path)
            except:
                pass
    
    def realtime_diarization(
        self,
        audio_chunk: np.ndarray,
        sample_rate: int = 16000
    ) -> Dict:
        """
        Perform real-time speaker diarization on audio chunk
        
        Args:
            audio_chunk: Audio array chunk
            sample_rate: Audio sample rate
            
        Returns:
            Dictionary with speaker information
        """
        # Save audio chunk to temporary file for processing
        import tempfile
        import soundfile as sf
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            sf.write(tmp.name, audio_chunk, sample_rate)
            tmp_path = tmp.name
        
        try:
            segments = self.diarize_audio(tmp_path)
            
            # Determine dominant speaker
            speaker_durations = {}
            for seg in segments:
                speaker = seg["speaker"]
                duration = seg["duration"]
                speaker_durations[speaker] = speaker_durations.get(speaker, 0) + duration
            
            dominant_speaker = max(speaker_durations, key=speaker_durations.get) if speaker_durations else None
            
            return {
                "segments": segments,
                "dominant_speaker": dominant_speaker,
                "num_speakers": len(set(s["speaker"] for s in segments)),
                "speaker_durations": speaker_durations
            }
            
        finally:
            # Clean up temporary file
            import os
            try:
                os.unlink(tmp_path)
            except:
                pass


def diarize_audio_file_advanced(
    audio_path: str,
    hf_token: Optional[str] = None,
    min_speakers: int = 1,
    max_speakers: int = 10
) -> List[Dict]:
    """
    Convenience function for advanced speaker diarization
    
    Args:
        audio_path: Path to audio file
        hf_token: HuggingFace token
        min_speakers: Minimum number of speakers
        max_speakers: Maximum number of speakers
        
    Returns:
        List of speaker segments
    """
    identifier = AdvancedSpeakerIdentifier(
        hf_token=hf_token,
        min_speakers=min_speakers,
        max_speakers=max_speakers
    )
    
    return identifier.diarize_audio(audio_path)


if __name__ == "__main__":
    """Test advanced speaker identification"""
    print("=" * 80)
    print("Advanced Speaker Identification Test")
    print("=" * 80)
    
    # Create test instance
    try:
        identifier = AdvancedSpeakerIdentifier()
        print("✅ Advanced speaker identifier initialized successfully")
        
        # Test with sample audio (requires actual audio file)
        import sys
        if len(sys.argv) > 1:
            audio_path = sys.argv[1]
            print(f"\n📁 Processing: {audio_path}")
            
            segments = identifier.diarize_audio(audio_path)
            
            print(f"\n👥 Speaker Segments:")
            for i, seg in enumerate(segments[:10]):  # Show first 10
                print(f"   {i+1}. {seg['speaker']}: {seg['start']:.2f}s - {seg['end']:.2f}s")
            
            if len(segments) > 10:
                print(f"   ... and {len(segments) - 10} more segments")
        else:
            print("\n💡 Usage: python advanced_speaker_identification.py <audio_file>")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
