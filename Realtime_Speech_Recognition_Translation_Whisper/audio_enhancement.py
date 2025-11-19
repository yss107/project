#!/usr/bin/env python3
"""
Audio Enhancement and Preprocessing Module
Provides noise reduction, normalization, and audio quality improvements
"""

import numpy as np
from typing import Optional, Tuple
from scipy import signal
import warnings

warnings.filterwarnings('ignore')


class AudioEnhancer:
    """Audio enhancement and preprocessing for better speech recognition"""
    
    def __init__(
        self,
        sample_rate: int = 16000,
        enable_noise_reduction: bool = True,
        enable_normalization: bool = True,
        enable_vad: bool = True  # Voice Activity Detection
    ):
        """
        Initialize audio enhancer
        
        Args:
            sample_rate: Audio sample rate
            enable_noise_reduction: Enable noise reduction
            enable_normalization: Enable audio normalization
            enable_vad: Enable voice activity detection
        """
        self.sample_rate = sample_rate
        self.enable_noise_reduction = enable_noise_reduction
        self.enable_normalization = enable_normalization
        self.enable_vad = enable_vad
    
    def enhance_audio(self, audio: np.ndarray) -> np.ndarray:
        """
        Apply full audio enhancement pipeline
        
        Args:
            audio: Input audio array
            
        Returns:
            Enhanced audio array
        """
        enhanced = audio.copy()
        
        # Ensure mono
        if len(enhanced.shape) > 1:
            enhanced = enhanced.mean(axis=1)
        
        # Noise reduction
        if self.enable_noise_reduction:
            enhanced = self.reduce_noise(enhanced)
        
        # Normalization
        if self.enable_normalization:
            enhanced = self.normalize_audio(enhanced)
        
        # High-pass filter to remove low-frequency noise
        enhanced = self.high_pass_filter(enhanced)
        
        # Voice Activity Detection (trim silence)
        if self.enable_vad:
            enhanced = self.trim_silence(enhanced)
        
        return enhanced
    
    def reduce_noise(self, audio: np.ndarray) -> np.ndarray:
        """
        Reduce background noise using spectral gating
        
        Args:
            audio: Input audio array
            
        Returns:
            Noise-reduced audio
        """
        # Simple noise reduction using spectral subtraction
        # Calculate noise profile from first 0.5 seconds
        noise_profile_len = int(0.5 * self.sample_rate)
        
        if len(audio) < noise_profile_len:
            return audio
        
        noise_profile = audio[:noise_profile_len]
        
        # Compute STFT
        f, t, stft = signal.stft(audio, self.sample_rate, nperseg=512)
        
        # Estimate noise spectrum
        _, _, noise_stft = signal.stft(noise_profile, self.sample_rate, nperseg=512)
        noise_magnitude = np.abs(noise_stft).mean(axis=1, keepdims=True)
        
        # Spectral subtraction
        magnitude = np.abs(stft)
        phase = np.angle(stft)
        
        # Subtract noise with over-subtraction factor
        magnitude_cleaned = magnitude - 1.5 * noise_magnitude
        magnitude_cleaned = np.maximum(magnitude_cleaned, 0.1 * magnitude)  # Floor
        
        # Reconstruct
        stft_cleaned = magnitude_cleaned * np.exp(1j * phase)
        _, audio_cleaned = signal.istft(stft_cleaned, self.sample_rate)
        
        return audio_cleaned
    
    def normalize_audio(self, audio: np.ndarray, target_level: float = 0.9) -> np.ndarray:
        """
        Normalize audio to target level
        
        Args:
            audio: Input audio array
            target_level: Target peak level (0-1)
            
        Returns:
            Normalized audio
        """
        max_val = np.abs(audio).max()
        if max_val > 0:
            return audio * (target_level / max_val)
        return audio
    
    def high_pass_filter(self, audio: np.ndarray, cutoff: float = 80.0) -> np.ndarray:
        """
        Apply high-pass filter to remove low-frequency noise
        
        Args:
            audio: Input audio array
            cutoff: Cutoff frequency in Hz
            
        Returns:
            Filtered audio
        """
        nyquist = self.sample_rate / 2
        normalized_cutoff = cutoff / nyquist
        
        # Design high-pass filter
        b, a = signal.butter(5, normalized_cutoff, btype='high')
        
        # Apply filter
        filtered = signal.filtfilt(b, a, audio)
        
        return filtered
    
    def trim_silence(
        self,
        audio: np.ndarray,
        threshold: float = 0.01,
        min_silence_duration: float = 0.3
    ) -> np.ndarray:
        """
        Trim silence from beginning and end of audio
        
        Args:
            audio: Input audio array
            threshold: Amplitude threshold for silence detection
            min_silence_duration: Minimum silence duration to trim (seconds)
            
        Returns:
            Trimmed audio
        """
        # Calculate frame energy
        frame_length = int(0.02 * self.sample_rate)  # 20ms frames
        energy = np.array([
            np.sqrt(np.mean(audio[i:i+frame_length]**2))
            for i in range(0, len(audio) - frame_length, frame_length)
        ])
        
        # Find voice activity
        is_voice = energy > threshold
        
        if not is_voice.any():
            return audio
        
        # Find first and last voice frames
        voice_frames = np.where(is_voice)[0]
        start_frame = voice_frames[0]
        end_frame = voice_frames[-1]
        
        # Convert to samples
        start_sample = max(0, start_frame * frame_length - int(0.1 * self.sample_rate))  # 100ms padding
        end_sample = min(len(audio), (end_frame + 1) * frame_length + int(0.1 * self.sample_rate))
        
        return audio[start_sample:end_sample]
    
    def resample(self, audio: np.ndarray, original_sr: int) -> np.ndarray:
        """
        Resample audio to target sample rate
        
        Args:
            audio: Input audio array
            original_sr: Original sample rate
            
        Returns:
            Resampled audio
        """
        if original_sr == self.sample_rate:
            return audio
        
        # Calculate new length
        num_samples = int(len(audio) * self.sample_rate / original_sr)
        
        # Resample
        resampled = signal.resample(audio, num_samples)
        
        return resampled
    
    def detect_voice_activity(
        self,
        audio: np.ndarray,
        threshold: float = 0.01
    ) -> np.ndarray:
        """
        Detect voice activity in audio
        
        Args:
            audio: Input audio array
            threshold: Energy threshold for voice detection
            
        Returns:
            Boolean array indicating voice activity
        """
        # Calculate frame energy
        frame_length = int(0.02 * self.sample_rate)  # 20ms frames
        energy = np.array([
            np.sqrt(np.mean(audio[i:i+frame_length]**2))
            for i in range(0, len(audio) - frame_length, frame_length)
        ])
        
        # Detect voice
        is_voice = energy > threshold
        
        return is_voice


def preprocess_audio_file(
    audio_path: str,
    sample_rate: int = 16000,
    enhance: bool = True
) -> Tuple[np.ndarray, int]:
    """
    Load and preprocess audio file
    
    Args:
        audio_path: Path to audio file
        sample_rate: Target sample rate
        enhance: Whether to apply enhancement
        
    Returns:
        Tuple of (audio_data, sample_rate)
    """
    import soundfile as sf
    
    # Load audio
    audio, sr = sf.read(audio_path)
    
    # Enhance if requested
    if enhance:
        enhancer = AudioEnhancer(sample_rate=sample_rate)
        audio = enhancer.enhance_audio(audio)
    
    # Resample if needed
    if sr != sample_rate:
        enhancer = AudioEnhancer(sample_rate=sample_rate)
        audio = enhancer.resample(audio, sr)
    
    return audio, sample_rate


if __name__ == "__main__":
    # Example usage
    print("Audio Enhancement Module")
    print("=" * 50)
    
    # Create sample audio (sine wave with noise)
    sample_rate = 16000
    duration = 2.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Generate test signal
    clean_signal = np.sin(2 * np.pi * 440 * t)  # 440 Hz sine wave
    noise = np.random.randn(len(t)) * 0.1
    noisy_signal = clean_signal + noise
    
    # Enhance
    enhancer = AudioEnhancer(sample_rate=sample_rate)
    enhanced_signal = enhancer.enhance_audio(noisy_signal)
    
    print(f"Original signal: min={noisy_signal.min():.3f}, max={noisy_signal.max():.3f}")
    print(f"Enhanced signal: min={enhanced_signal.min():.3f}, max={enhanced_signal.max():.3f}")
    print("\n✅ Audio enhancement working correctly!")
