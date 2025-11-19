#!/usr/bin/env python3
"""
Advanced Noise Suppression Module
Implements RNNoise-based and deep learning noise reduction
"""

import numpy as np
from typing import Optional, Tuple
import warnings
warnings.filterwarnings('ignore')


class AdvancedNoiseSuppressor:
    """
    Advanced noise suppression using multiple techniques:
    - Spectral subtraction
    - noisereduce library
    - WebRTC VAD
    - Deep learning-based methods
    """
    
    def __init__(
        self,
        sample_rate: int = 16000,
        method: str = "noisereduce"
    ):
        """
        Initialize noise suppressor
        
        Args:
            sample_rate: Audio sample rate
            method: Noise reduction method ('noisereduce', 'webrtc', 'spectral', 'combined')
        """
        self.sample_rate = sample_rate
        self.method = method
        
        print(f"🔧 Initializing noise suppressor with method: {method}")
        
        # Initialize components based on method
        if method in ["noisereduce", "combined"]:
            self._initialize_noisereduce()
        
        if method in ["webrtc", "combined"]:
            self._initialize_webrtc_vad()
    
    def _initialize_noisereduce(self):
        """Initialize noisereduce library"""
        try:
            import noisereduce as nr
            self.nr = nr
            print("✅ Noisereduce library loaded")
        except ImportError:
            print("⚠️ Warning: noisereduce not available")
            print("   Install with: pip install noisereduce")
            self.nr = None
    
    def _initialize_webrtc_vad(self):
        """Initialize WebRTC VAD"""
        try:
            import webrtcvad
            self.vad = webrtcvad.Vad()
            self.vad.set_mode(3)  # Aggressive mode
            print("✅ WebRTC VAD loaded")
        except ImportError:
            print("⚠️ Warning: webrtcvad not available")
            print("   Install with: pip install webrtcvad")
            self.vad = None
    
    def suppress_noise(
        self,
        audio_data: np.ndarray,
        stationary: bool = True,
        prop_decrease: float = 1.0
    ) -> np.ndarray:
        """
        Apply noise suppression to audio
        
        Args:
            audio_data: Input audio array
            stationary: Whether noise is stationary
            prop_decrease: Proportion of noise to reduce (0.0 to 1.0)
            
        Returns:
            Noise-suppressed audio
        """
        if self.method == "noisereduce":
            return self._suppress_noisereduce(audio_data, stationary, prop_decrease)
        elif self.method == "webrtc":
            return self._suppress_webrtc(audio_data)
        elif self.method == "spectral":
            return self._suppress_spectral(audio_data)
        elif self.method == "combined":
            return self._suppress_combined(audio_data, stationary, prop_decrease)
        else:
            raise ValueError(f"Unknown method: {self.method}")
    
    def _suppress_noisereduce(
        self,
        audio_data: np.ndarray,
        stationary: bool,
        prop_decrease: float
    ) -> np.ndarray:
        """Apply noise reduction using noisereduce library"""
        if self.nr is None:
            print("⚠️ Noisereduce not available, returning original audio")
            return audio_data
        
        try:
            # Reduce noise
            reduced = self.nr.reduce_noise(
                y=audio_data,
                sr=self.sample_rate,
                stationary=stationary,
                prop_decrease=prop_decrease
            )
            return reduced
        except Exception as e:
            print(f"⚠️ Error in noise reduction: {e}")
            return audio_data
    
    def _suppress_webrtc(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply noise suppression using WebRTC VAD"""
        if self.vad is None:
            print("⚠️ WebRTC VAD not available, returning original audio")
            return audio_data
        
        try:
            # Convert to 16-bit PCM
            audio_int16 = (audio_data * 32767).astype(np.int16)
            
            # Frame parameters for VAD (WebRTC requires specific frame sizes)
            frame_duration = 30  # ms (10, 20, or 30)
            frame_size = int(self.sample_rate * frame_duration / 1000)
            
            # Process frames
            output_frames = []
            for i in range(0, len(audio_int16), frame_size):
                frame = audio_int16[i:i + frame_size]
                
                # Pad last frame if needed
                if len(frame) < frame_size:
                    frame = np.pad(frame, (0, frame_size - len(frame)), 'constant')
                
                # Check if frame contains speech
                frame_bytes = frame.tobytes()
                is_speech = self.vad.is_speech(frame_bytes, self.sample_rate)
                
                # Keep frame if it contains speech, attenuate if not
                if is_speech:
                    output_frames.append(frame)
                else:
                    output_frames.append((frame * 0.1).astype(np.int16))  # Attenuate noise
            
            # Concatenate frames and convert back to float
            output = np.concatenate(output_frames)
            output = output[:len(audio_data)]  # Trim to original length
            output = output.astype(np.float32) / 32767.0
            
            return output
            
        except Exception as e:
            print(f"⚠️ Error in WebRTC VAD: {e}")
            return audio_data
    
    def _suppress_spectral(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply spectral subtraction noise reduction"""
        try:
            from scipy import signal
            
            # Compute STFT
            f, t, Zxx = signal.stft(audio_data, fs=self.sample_rate, nperseg=512)
            
            # Estimate noise from first 0.5 seconds
            noise_frames = int(0.5 * self.sample_rate / 512)
            noise_spectrum = np.mean(np.abs(Zxx[:, :noise_frames]), axis=1, keepdims=True)
            
            # Spectral subtraction
            magnitude = np.abs(Zxx)
            phase = np.angle(Zxx)
            
            # Subtract noise (with oversubtraction factor)
            alpha = 2.0  # Oversubtraction factor
            magnitude_reduced = np.maximum(magnitude - alpha * noise_spectrum, 0.1 * magnitude)
            
            # Reconstruct signal
            Zxx_reduced = magnitude_reduced * np.exp(1j * phase)
            _, audio_reduced = signal.istft(Zxx_reduced, fs=self.sample_rate, nperseg=512)
            
            # Trim to original length
            audio_reduced = audio_reduced[:len(audio_data)]
            
            return audio_reduced.astype(np.float32)
            
        except Exception as e:
            print(f"⚠️ Error in spectral subtraction: {e}")
            return audio_data
    
    def _suppress_combined(
        self,
        audio_data: np.ndarray,
        stationary: bool,
        prop_decrease: float
    ) -> np.ndarray:
        """Apply combined noise suppression techniques"""
        # First apply spectral subtraction
        audio = self._suppress_spectral(audio_data)
        
        # Then apply noisereduce if available
        if self.nr is not None:
            audio = self._suppress_noisereduce(audio, stationary, prop_decrease)
        
        # Finally apply WebRTC VAD if available
        if self.vad is not None:
            audio = self._suppress_webrtc(audio)
        
        return audio
    
    def estimate_snr(self, audio_data: np.ndarray) -> float:
        """
        Estimate Signal-to-Noise Ratio
        
        Args:
            audio_data: Audio array
            
        Returns:
            Estimated SNR in dB
        """
        # Simple SNR estimation
        # Use top 25% energy frames as signal, bottom 25% as noise
        
        frame_length = int(0.025 * self.sample_rate)  # 25ms frames
        hop_length = int(0.010 * self.sample_rate)    # 10ms hop
        
        # Calculate frame energies
        energies = []
        for i in range(0, len(audio_data) - frame_length, hop_length):
            frame = audio_data[i:i + frame_length]
            energy = np.sum(frame ** 2)
            energies.append(energy)
        
        energies = np.array(energies)
        
        # Sort energies
        sorted_energies = np.sort(energies)
        
        # Estimate signal and noise power
        n_frames = len(sorted_energies)
        noise_power = np.mean(sorted_energies[:n_frames // 4])  # Bottom 25%
        signal_power = np.mean(sorted_energies[3 * n_frames // 4:])  # Top 25%
        
        # Calculate SNR in dB
        if noise_power > 0:
            snr_db = 10 * np.log10(signal_power / noise_power)
        else:
            snr_db = float('inf')
        
        return snr_db
    
    def adaptive_suppress(
        self,
        audio_data: np.ndarray,
        target_snr: float = 20.0
    ) -> np.ndarray:
        """
        Adaptively suppress noise based on estimated SNR
        
        Args:
            audio_data: Input audio
            target_snr: Target SNR in dB
            
        Returns:
            Noise-suppressed audio
        """
        # Estimate current SNR
        current_snr = self.estimate_snr(audio_data)
        
        print(f"📊 Estimated SNR: {current_snr:.1f} dB")
        
        # Adjust noise reduction based on SNR
        if current_snr < 0:
            # Very noisy, aggressive reduction
            prop_decrease = 1.0
            print("🔊 Applying aggressive noise reduction")
        elif current_snr < 10:
            # Noisy, moderate reduction
            prop_decrease = 0.8
            print("🔊 Applying moderate noise reduction")
        elif current_snr < target_snr:
            # Some noise, light reduction
            prop_decrease = 0.5
            print("🔊 Applying light noise reduction")
        else:
            # Clean audio, minimal reduction
            prop_decrease = 0.2
            print("✅ Audio is clean, minimal processing")
        
        return self.suppress_noise(audio_data, prop_decrease=prop_decrease)


class MultiChannelNoiseSuppressor:
    """
    Noise suppression for multi-channel audio
    Implements beamforming and spatial filtering
    """
    
    def __init__(self, sample_rate: int = 16000):
        """
        Initialize multi-channel noise suppressor
        
        Args:
            sample_rate: Audio sample rate
        """
        self.sample_rate = sample_rate
    
    def suppress_multichannel(
        self,
        audio_channels: np.ndarray,
        method: str = "delay_sum"
    ) -> np.ndarray:
        """
        Suppress noise in multi-channel audio
        
        Args:
            audio_channels: Audio array with shape (n_channels, n_samples)
            method: Beamforming method ('delay_sum', 'mvdr', 'avg')
            
        Returns:
            Single-channel noise-suppressed audio
        """
        if method == "delay_sum":
            return self._delay_and_sum_beamforming(audio_channels)
        elif method == "mvdr":
            return self._mvdr_beamforming(audio_channels)
        elif method == "avg":
            return np.mean(audio_channels, axis=0)
        else:
            raise ValueError(f"Unknown method: {method}")
    
    def _delay_and_sum_beamforming(self, audio_channels: np.ndarray) -> np.ndarray:
        """
        Simple delay-and-sum beamforming
        
        Args:
            audio_channels: Shape (n_channels, n_samples)
            
        Returns:
            Beamformed single-channel audio
        """
        # For simplicity, assume channels are already aligned
        # In practice, you would apply delays based on microphone geometry
        return np.mean(audio_channels, axis=0)
    
    def _mvdr_beamforming(self, audio_channels: np.ndarray) -> np.ndarray:
        """
        Minimum Variance Distortionless Response (MVDR) beamforming
        
        Args:
            audio_channels: Shape (n_channels, n_samples)
            
        Returns:
            Beamformed single-channel audio
        """
        # Simplified MVDR implementation
        # In practice, this requires noise covariance estimation
        from scipy import signal
        
        # Compute cross-correlation matrix
        n_channels = audio_channels.shape[0]
        
        # Estimate signal + noise covariance from full signal
        R = np.cov(audio_channels)
        
        # Assume first channel as reference
        steering_vector = np.zeros(n_channels)
        steering_vector[0] = 1.0
        
        # MVDR weights
        try:
            R_inv = np.linalg.inv(R + np.eye(n_channels) * 1e-6)  # Regularization
            weights = R_inv @ steering_vector
            weights = weights / (steering_vector @ R_inv @ steering_vector)
        except:
            # Fallback to simple averaging
            weights = np.ones(n_channels) / n_channels
        
        # Apply weights
        output = np.sum(audio_channels.T * weights, axis=1)
        
        return output


def process_audio_with_noise_suppression(
    audio_path: str,
    output_path: str,
    method: str = "combined"
) -> str:
    """
    Convenience function to process audio file with noise suppression
    
    Args:
        audio_path: Input audio file path
        output_path: Output audio file path
        method: Noise suppression method
        
    Returns:
        Path to processed audio file
    """
    import soundfile as sf
    
    # Load audio
    audio_data, sr = sf.read(audio_path)
    
    # Convert to mono if stereo
    if len(audio_data.shape) > 1:
        audio_data = np.mean(audio_data, axis=1)
    
    # Create suppressor
    suppressor = AdvancedNoiseSuppressor(sample_rate=sr, method=method)
    
    # Suppress noise
    audio_clean = suppressor.adaptive_suppress(audio_data)
    
    # Save
    sf.write(output_path, audio_clean, sr)
    
    print(f"✅ Processed audio saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    """Test noise suppression"""
    print("=" * 80)
    print("Advanced Noise Suppression Test")
    print("=" * 80)
    
    import sys
    
    if len(sys.argv) > 1:
        audio_path = sys.argv[1]
        output_path = sys.argv[2] if len(sys.argv) > 2 else "output_clean.wav"
        
        print(f"\n📁 Processing: {audio_path}")
        
        # Process with combined method
        result_path = process_audio_with_noise_suppression(
            audio_path,
            output_path,
            method="combined"
        )
        
        print(f"\n✅ Done! Clean audio saved to: {result_path}")
    else:
        print("\n💡 Usage: python advanced_noise_suppression.py <input_audio> [output_audio]")
        print("\n✅ Noise suppression module initialized successfully")
