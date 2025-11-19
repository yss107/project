#!/usr/bin/env python3
"""
Multi-Channel Audio Support
Handles recording, processing, and beamforming for multi-channel audio
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')


class MultiChannelAudioProcessor:
    """
    Process multi-channel audio with beamforming and spatial filtering
    """
    
    def __init__(
        self,
        n_channels: int = 2,
        sample_rate: int = 16000,
        beamforming_method: str = "delay_sum"
    ):
        """
        Initialize multi-channel audio processor
        
        Args:
            n_channels: Number of audio channels
            sample_rate: Audio sample rate
            beamforming_method: Beamforming method ('delay_sum', 'mvdr', 'gsc')
        """
        self.n_channels = n_channels
        self.sample_rate = sample_rate
        self.beamforming_method = beamforming_method
        
        print(f"🎙️ Multi-channel processor initialized: {n_channels} channels @ {sample_rate} Hz")
        print(f"   Beamforming method: {beamforming_method}")
    
    def record_multichannel(
        self,
        duration: float = 5.0,
        device: Optional[int] = None
    ) -> np.ndarray:
        """
        Record multi-channel audio
        
        Args:
            duration: Recording duration in seconds
            device: Audio device index (None for default)
            
        Returns:
            Audio array with shape (n_samples, n_channels)
        """
        try:
            import sounddevice as sd
            
            print(f"🎤 Recording {duration}s of {self.n_channels}-channel audio...")
            
            audio = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.n_channels,
                device=device,
                dtype='float32'
            )
            sd.wait()
            
            print(f"✅ Recording complete: {audio.shape}")
            return audio
            
        except ImportError:
            raise ImportError("sounddevice not available. Install with: pip install sounddevice")
    
    def load_multichannel_audio(
        self,
        audio_path: str
    ) -> Tuple[np.ndarray, int]:
        """
        Load multi-channel audio from file
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Tuple of (audio_data, sample_rate)
            audio_data has shape (n_samples, n_channels)
        """
        import soundfile as sf
        
        audio, sr = sf.read(audio_path, always_2d=True)
        
        print(f"📁 Loaded {audio_path}")
        print(f"   Shape: {audio.shape}, Sample rate: {sr} Hz")
        
        # Resample if needed
        if sr != self.sample_rate:
            print(f"🔄 Resampling from {sr} Hz to {self.sample_rate} Hz...")
            from scipy import signal
            
            n_samples_new = int(len(audio) * self.sample_rate / sr)
            audio_resampled = np.zeros((n_samples_new, audio.shape[1]))
            
            for ch in range(audio.shape[1]):
                audio_resampled[:, ch] = signal.resample(audio[:, ch], n_samples_new)
            
            audio = audio_resampled
            sr = self.sample_rate
        
        return audio, sr
    
    def apply_beamforming(
        self,
        audio_channels: np.ndarray,
        target_angle: Optional[float] = None
    ) -> np.ndarray:
        """
        Apply beamforming to multi-channel audio
        
        Args:
            audio_channels: Audio with shape (n_samples, n_channels)
            target_angle: Target direction in degrees (0 = front, None = auto)
            
        Returns:
            Single-channel beamformed audio
        """
        # Transpose to (n_channels, n_samples) for processing
        audio_t = audio_channels.T
        
        if self.beamforming_method == "delay_sum":
            output = self._delay_and_sum_beamforming(audio_t, target_angle)
        elif self.beamforming_method == "mvdr":
            output = self._mvdr_beamforming(audio_t)
        elif self.beamforming_method == "gsc":
            output = self._gsc_beamforming(audio_t, target_angle)
        else:
            # Default: simple averaging
            output = np.mean(audio_t, axis=0)
        
        return output
    
    def _delay_and_sum_beamforming(
        self,
        audio_channels: np.ndarray,
        target_angle: Optional[float] = None
    ) -> np.ndarray:
        """
        Delay-and-Sum beamforming
        
        Args:
            audio_channels: Shape (n_channels, n_samples)
            target_angle: Target direction in degrees
            
        Returns:
            Beamformed audio
        """
        n_channels, n_samples = audio_channels.shape
        
        if target_angle is None or n_channels < 2:
            # No steering, just sum
            return np.mean(audio_channels, axis=0)
        
        # Assume linear array with spacing d
        d = 0.05  # 5cm spacing between microphones
        c = 343.0  # Speed of sound in m/s
        
        # Calculate delays for each channel
        angle_rad = np.radians(target_angle)
        delays = np.zeros(n_channels)
        
        for i in range(n_channels):
            delays[i] = (i * d * np.sin(angle_rad)) / c
        
        # Convert delays to samples
        delay_samples = (delays * self.sample_rate).astype(int)
        
        # Apply delays and sum
        output = np.zeros(n_samples)
        for i, delay in enumerate(delay_samples):
            if delay >= 0:
                output[delay:] += audio_channels[i, :n_samples - delay]
            else:
                output[:n_samples + delay] += audio_channels[i, -delay:]
        
        output /= n_channels
        return output
    
    def _mvdr_beamforming(self, audio_channels: np.ndarray) -> np.ndarray:
        """
        Minimum Variance Distortionless Response (MVDR) beamforming
        
        Args:
            audio_channels: Shape (n_channels, n_samples)
            
        Returns:
            Beamformed audio
        """
        n_channels, n_samples = audio_channels.shape
        
        # Estimate covariance matrix
        R = np.cov(audio_channels)
        
        # Steering vector (assume target from first channel)
        a = np.zeros(n_channels)
        a[0] = 1.0
        
        try:
            # MVDR beamformer weights
            R_inv = np.linalg.inv(R + np.eye(n_channels) * 1e-6)
            w = R_inv @ a / (a @ R_inv @ a)
            
            # Apply weights
            output = w @ audio_channels
            
        except np.linalg.LinAlgError:
            # Fallback to simple averaging
            print("⚠️ MVDR failed, using simple averaging")
            output = np.mean(audio_channels, axis=0)
        
        return output
    
    def _gsc_beamforming(
        self,
        audio_channels: np.ndarray,
        target_angle: Optional[float] = None
    ) -> np.ndarray:
        """
        Generalized Sidelobe Canceller (GSC) beamforming
        
        Args:
            audio_channels: Shape (n_channels, n_samples)
            target_angle: Target direction in degrees
            
        Returns:
            Beamformed audio
        """
        # Start with delay-and-sum
        output = self._delay_and_sum_beamforming(audio_channels, target_angle)
        
        # TODO: Implement adaptive interference cancellation
        # For now, just return delay-and-sum result
        
        return output
    
    def extract_spatial_features(
        self,
        audio_channels: np.ndarray
    ) -> Dict[str, float]:
        """
        Extract spatial audio features
        
        Args:
            audio_channels: Shape (n_samples, n_channels)
            
        Returns:
            Dictionary of spatial features
        """
        if audio_channels.shape[1] < 2:
            return {"interchannel_correlation": 1.0}
        
        # Interchannel correlation
        correlations = []
        for i in range(audio_channels.shape[1] - 1):
            corr = np.corrcoef(audio_channels[:, i], audio_channels[:, i + 1])[0, 1]
            correlations.append(corr)
        
        # Interchannel level difference
        levels = [np.sqrt(np.mean(audio_channels[:, i] ** 2)) for i in range(audio_channels.shape[1])]
        ild = np.max(levels) / (np.min(levels) + 1e-10)
        
        # Interchannel time difference (simplified)
        from scipy import signal
        xcorr = signal.correlate(audio_channels[:, 0], audio_channels[:, 1], mode='same')
        itd_samples = np.argmax(xcorr) - len(xcorr) // 2
        itd_ms = (itd_samples / self.sample_rate) * 1000
        
        return {
            "interchannel_correlation": float(np.mean(correlations)),
            "interchannel_level_difference_db": float(20 * np.log10(ild)),
            "interchannel_time_difference_ms": float(itd_ms),
            "n_channels": audio_channels.shape[1]
        }
    
    def estimate_direction_of_arrival(
        self,
        audio_channels: np.ndarray,
        mic_spacing: float = 0.05
    ) -> float:
        """
        Estimate direction of arrival (DOA) of sound source
        
        Args:
            audio_channels: Shape (n_samples, n_channels)
            mic_spacing: Distance between microphones in meters
            
        Returns:
            Estimated angle in degrees (0 = front, positive = right)
        """
        if audio_channels.shape[1] < 2:
            return 0.0
        
        from scipy import signal
        
        # Use first two channels for DOA estimation
        ch1 = audio_channels[:, 0]
        ch2 = audio_channels[:, 1]
        
        # Cross-correlation
        correlation = signal.correlate(ch1, ch2, mode='same')
        delay_samples = np.argmax(correlation) - len(correlation) // 2
        
        # Convert to time delay
        delay_seconds = delay_samples / self.sample_rate
        
        # Calculate angle
        c = 343.0  # Speed of sound in m/s
        sin_angle = (delay_seconds * c) / mic_spacing
        
        # Clamp to valid range
        sin_angle = np.clip(sin_angle, -1.0, 1.0)
        
        angle_rad = np.arcsin(sin_angle)
        angle_deg = np.degrees(angle_rad)
        
        return float(angle_deg)
    
    def process_realtime(
        self,
        callback,
        duration: Optional[float] = None,
        device: Optional[int] = None
    ):
        """
        Process multi-channel audio in real-time
        
        Args:
            callback: Function to call with beamformed audio chunks
            duration: Total duration (None = infinite)
            device: Audio device index
        """
        try:
            import sounddevice as sd
            
            print(f"🎤 Starting real-time {self.n_channels}-channel processing...")
            
            def audio_callback(indata, frames, time, status):
                if status:
                    print(f"⚠️ Status: {status}")
                
                # Apply beamforming
                beamformed = self.apply_beamforming(indata)
                
                # Call user callback
                callback(beamformed)
            
            # Start stream
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.n_channels,
                callback=audio_callback,
                device=device
            ):
                if duration:
                    sd.sleep(int(duration * 1000))
                else:
                    print("Press Ctrl+C to stop...")
                    sd.sleep(10000000)  # Very long sleep
            
        except KeyboardInterrupt:
            print("\n⏹️ Stopped")
        except ImportError:
            raise ImportError("sounddevice not available. Install with: pip install sounddevice")


def save_multichannel_audio(
    audio_data: np.ndarray,
    output_path: str,
    sample_rate: int = 16000
):
    """
    Save multi-channel audio to file
    
    Args:
        audio_data: Audio with shape (n_samples, n_channels)
        output_path: Output file path
        sample_rate: Sample rate
    """
    import soundfile as sf
    
    sf.write(output_path, audio_data, sample_rate)
    print(f"✅ Saved multi-channel audio to: {output_path}")


if __name__ == "__main__":
    """Test multi-channel audio processing"""
    print("=" * 80)
    print("Multi-Channel Audio Processing Test")
    print("=" * 80)
    
    import sys
    
    if len(sys.argv) > 1:
        # Process audio file
        audio_path = sys.argv[1]
        
        print(f"\n📁 Processing: {audio_path}")
        
        # Create processor
        processor = MultiChannelAudioProcessor(n_channels=2, beamforming_method="mvdr")
        
        # Load audio
        audio, sr = processor.load_multichannel_audio(audio_path)
        
        # Extract spatial features
        features = processor.extract_spatial_features(audio)
        print("\n📊 Spatial Features:")
        for key, value in features.items():
            print(f"   {key}: {value:.3f}")
        
        # Estimate DOA
        doa = processor.estimate_direction_of_arrival(audio)
        print(f"\n🎯 Direction of Arrival: {doa:.1f}°")
        
        # Apply beamforming
        beamformed = processor.apply_beamforming(audio)
        
        # Save result
        output_path = "output_beamformed.wav"
        import soundfile as sf
        sf.write(output_path, beamformed, sr)
        print(f"\n✅ Beamformed audio saved to: {output_path}")
        
    else:
        print("\n💡 Usage: python multichannel_audio.py <audio_file>")
        print("\n✅ Multi-channel audio module initialized successfully")
        
        # Show available audio devices
        try:
            import sounddevice as sd
            print("\n🎙️ Available audio devices:")
            print(sd.query_devices())
        except:
            pass
