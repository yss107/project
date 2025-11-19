#!/usr/bin/env python3
"""
Advanced Emotion Detection using Deep Learning
Uses wav2vec2 and SpeechBrain for state-of-the-art emotion recognition
"""

import numpy as np
import torch
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')


class AdvancedEmotionDetector:
    """
    Advanced emotion detection using deep learning models
    Supports wav2vec2 and SpeechBrain models
    """
    
    # Emotion labels
    EMOTIONS = ["neutral", "happy", "sad", "angry", "fear", "disgust", "surprise"]
    
    def __init__(
        self,
        device: str = "auto",
        model_type: str = "speechbrain",
        sample_rate: int = 16000
    ):
        """
        Initialize advanced emotion detector
        
        Args:
            device: Device to run model on ('cuda', 'cpu', or 'auto')
            model_type: Type of model to use ('speechbrain' or 'wav2vec2')
            sample_rate: Audio sample rate
        """
        # Determine device
        if device == "auto":
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
        
        print(f"🔧 Initializing emotion detector on {self.device}")
        
        self.model_type = model_type
        self.sample_rate = sample_rate
        
        # Initialize model
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize emotion detection model"""
        if self.model_type == "speechbrain":
            self._initialize_speechbrain()
        elif self.model_type == "wav2vec2":
            self._initialize_wav2vec2()
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
    
    def _initialize_speechbrain(self):
        """Initialize SpeechBrain emotion recognition model"""
        try:
            from speechbrain.pretrained import EncoderClassifier
            
            print("📥 Loading SpeechBrain emotion recognition model...")
            
            # Load pre-trained emotion recognition model
            self.classifier = EncoderClassifier.from_hparams(
                source="speechbrain/emotion-recognition-wav2vec2-IEMOCAP",
                savedir="pretrained_models/emotion_recognition",
                run_opts={"device": str(self.device)}
            )
            
            # Emotion mapping for IEMOCAP dataset
            self.emotion_map = {
                0: "neutral",
                1: "happy",
                2: "sad",
                3: "angry"
            }
            
            print("✅ SpeechBrain emotion model loaded successfully")
            
        except ImportError as e:
            print(f"⚠️ Warning: SpeechBrain not available: {e}")
            print("   Install with: pip install speechbrain")
            self.classifier = None
        except Exception as e:
            print(f"⚠️ Warning: Could not initialize SpeechBrain model: {e}")
            self.classifier = None
    
    def _initialize_wav2vec2(self):
        """Initialize wav2vec2-based emotion recognition model"""
        try:
            from transformers import Wav2Vec2ForSequenceClassification, Wav2Vec2FeatureExtractor
            
            print("📥 Loading wav2vec2 emotion recognition model...")
            
            # Load pre-trained model from HuggingFace
            model_name = "ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition"
            
            self.feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(model_name)
            self.classifier = Wav2Vec2ForSequenceClassification.from_pretrained(model_name)
            
            if self.device.type == "cuda":
                self.classifier.to(self.device)
            
            # Emotion mapping
            self.emotion_map = {
                0: "angry",
                1: "disgust",
                2: "fear",
                3: "happy",
                4: "neutral",
                5: "sad",
                6: "surprise"
            }
            
            print("✅ Wav2vec2 emotion model loaded successfully")
            
        except ImportError as e:
            print(f"⚠️ Warning: Transformers not available: {e}")
            print("   Install with: pip install transformers")
            self.classifier = None
        except Exception as e:
            print(f"⚠️ Warning: Could not initialize wav2vec2 model: {e}")
            self.classifier = None
    
    def detect_emotion(
        self,
        audio_data: np.ndarray,
        return_all_scores: bool = False
    ) -> Dict:
        """
        Detect emotion from audio data
        
        Args:
            audio_data: Audio array (mono, sample_rate Hz)
            return_all_scores: Whether to return scores for all emotions
            
        Returns:
            Dictionary with emotion prediction and confidence
        """
        if self.classifier is None:
            raise RuntimeError("Emotion detection model not initialized")
        
        # Ensure audio is in correct format
        audio_data = audio_data.astype(np.float32)
        
        if self.model_type == "speechbrain":
            return self._detect_emotion_speechbrain(audio_data, return_all_scores)
        elif self.model_type == "wav2vec2":
            return self._detect_emotion_wav2vec2(audio_data, return_all_scores)
    
    def _detect_emotion_speechbrain(
        self,
        audio_data: np.ndarray,
        return_all_scores: bool
    ) -> Dict:
        """Detect emotion using SpeechBrain"""
        import torch
        
        # Convert to tensor
        audio_tensor = torch.tensor(audio_data).unsqueeze(0).to(self.device)
        
        # Get prediction
        with torch.no_grad():
            output_prob, score, index, text_lab = self.classifier.classify_batch(audio_tensor)
        
        # Get emotion label and confidence
        emotion_idx = index.item()
        emotion = self.emotion_map.get(emotion_idx, "unknown")
        confidence = score.max().item()
        
        result = {
            "emotion": emotion,
            "confidence": confidence,
            "model": "speechbrain"
        }
        
        if return_all_scores:
            result["all_scores"] = {
                self.emotion_map.get(i, f"emotion_{i}"): output_prob[0, i].item()
                for i in range(output_prob.shape[1])
            }
        
        return result
    
    def _detect_emotion_wav2vec2(
        self,
        audio_data: np.ndarray,
        return_all_scores: bool
    ) -> Dict:
        """Detect emotion using wav2vec2"""
        import torch
        
        # Extract features
        inputs = self.feature_extractor(
            audio_data,
            sampling_rate=self.sample_rate,
            return_tensors="pt",
            padding=True
        )
        
        # Move to device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Get prediction
        with torch.no_grad():
            logits = self.classifier(**inputs).logits
        
        # Get probabilities
        probs = torch.nn.functional.softmax(logits, dim=-1)
        
        # Get top prediction
        predicted_idx = torch.argmax(probs, dim=-1).item()
        confidence = probs[0, predicted_idx].item()
        
        emotion = self.emotion_map.get(predicted_idx, "unknown")
        
        result = {
            "emotion": emotion,
            "confidence": confidence,
            "model": "wav2vec2"
        }
        
        if return_all_scores:
            result["all_scores"] = {
                self.emotion_map.get(i, f"emotion_{i}"): probs[0, i].item()
                for i in range(probs.shape[1])
            }
        
        return result
    
    def detect_emotion_batch(
        self,
        audio_batch: List[np.ndarray]
    ) -> List[Dict]:
        """
        Detect emotions for a batch of audio segments
        
        Args:
            audio_batch: List of audio arrays
            
        Returns:
            List of emotion predictions
        """
        results = []
        for audio in audio_batch:
            try:
                result = self.detect_emotion(audio)
                results.append(result)
            except Exception as e:
                print(f"⚠️ Error processing audio segment: {e}")
                results.append({
                    "emotion": "error",
                    "confidence": 0.0,
                    "error": str(e)
                })
        
        return results
    
    def analyze_emotional_trajectory(
        self,
        audio_data: np.ndarray,
        window_size: float = 3.0,
        hop_size: float = 1.0
    ) -> List[Dict]:
        """
        Analyze emotional changes over time
        
        Args:
            audio_data: Full audio array
            window_size: Window size in seconds
            hop_size: Hop size in seconds
            
        Returns:
            List of emotion predictions over time
        """
        window_samples = int(window_size * self.sample_rate)
        hop_samples = int(hop_size * self.sample_rate)
        
        trajectory = []
        
        for start in range(0, len(audio_data) - window_samples, hop_samples):
            end = start + window_samples
            window = audio_data[start:end]
            
            result = self.detect_emotion(window)
            result["timestamp"] = start / self.sample_rate
            result["duration"] = window_size
            
            trajectory.append(result)
        
        return trajectory


class EmotionFeatureExtractor:
    """
    Extract acoustic features for emotion analysis
    """
    
    def __init__(self, sample_rate: int = 16000):
        """
        Initialize feature extractor
        
        Args:
            sample_rate: Audio sample rate
        """
        self.sample_rate = sample_rate
    
    def extract_prosodic_features(self, audio_data: np.ndarray) -> Dict[str, float]:
        """
        Extract prosodic features related to emotion
        
        Args:
            audio_data: Audio array
            
        Returns:
            Dictionary of prosodic features
        """
        from scipy import signal, stats
        
        # Energy features
        energy = np.sum(audio_data ** 2) / len(audio_data)
        
        # Zero crossing rate
        zcr = np.sum(np.abs(np.diff(np.sign(audio_data)))) / (2 * len(audio_data))
        
        # Pitch estimation using autocorrelation
        correlation = np.correlate(audio_data, audio_data, mode='full')
        correlation = correlation[len(correlation)//2:]
        
        # Find peaks in autocorrelation
        peaks, _ = signal.find_peaks(correlation)
        if len(peaks) > 0:
            pitch_period = peaks[0] if peaks[0] > 0 else 1
            pitch_freq = self.sample_rate / pitch_period
        else:
            pitch_freq = 0
        
        # Spectral features
        fft = np.fft.rfft(audio_data)
        magnitude = np.abs(fft)
        
        # Spectral centroid
        freqs = np.fft.rfftfreq(len(audio_data), 1/self.sample_rate)
        spectral_centroid = np.sum(freqs * magnitude) / np.sum(magnitude) if np.sum(magnitude) > 0 else 0
        
        # Spectral spread
        spectral_spread = np.sqrt(
            np.sum(((freqs - spectral_centroid) ** 2) * magnitude) / np.sum(magnitude)
        ) if np.sum(magnitude) > 0 else 0
        
        return {
            "energy": float(energy),
            "zero_crossing_rate": float(zcr),
            "pitch_frequency": float(pitch_freq),
            "spectral_centroid": float(spectral_centroid),
            "spectral_spread": float(spectral_spread)
        }


def detect_emotion_from_file(
    audio_path: str,
    model_type: str = "speechbrain",
    return_trajectory: bool = False
) -> Dict:
    """
    Convenience function to detect emotion from audio file
    
    Args:
        audio_path: Path to audio file
        model_type: Type of model to use
        return_trajectory: Whether to return emotional trajectory
        
    Returns:
        Emotion detection result
    """
    import soundfile as sf
    
    # Load audio
    audio_data, sr = sf.read(audio_path)
    
    # Convert to mono if stereo
    if len(audio_data.shape) > 1:
        audio_data = np.mean(audio_data, axis=1)
    
    # Resample if needed
    if sr != 16000:
        from scipy import signal
        audio_data = signal.resample(
            audio_data,
            int(len(audio_data) * 16000 / sr)
        )
    
    # Create detector
    detector = AdvancedEmotionDetector(model_type=model_type, sample_rate=16000)
    
    if return_trajectory:
        return detector.analyze_emotional_trajectory(audio_data)
    else:
        return detector.detect_emotion(audio_data, return_all_scores=True)


if __name__ == "__main__":
    """Test advanced emotion detection"""
    print("=" * 80)
    print("Advanced Emotion Detection Test")
    print("=" * 80)
    
    # Test with SpeechBrain
    try:
        print("\n1. Testing SpeechBrain model...")
        detector = AdvancedEmotionDetector(model_type="speechbrain")
        print("✅ SpeechBrain detector initialized")
        
        # Test with sample audio
        import sys
        if len(sys.argv) > 1:
            audio_path = sys.argv[1]
            print(f"\n📁 Processing: {audio_path}")
            
            result = detect_emotion_from_file(audio_path, model_type="speechbrain")
            
            print(f"\n😊 Emotion: {result['emotion'].capitalize()}")
            print(f"   Confidence: {result['confidence']:.2%}")
            
            if "all_scores" in result:
                print("\n   All scores:")
                for emotion, score in result["all_scores"].items():
                    print(f"     {emotion}: {score:.2%}")
        
    except Exception as e:
        print(f"❌ Error with SpeechBrain: {e}")
    
    # Test with wav2vec2
    try:
        print("\n2. Testing wav2vec2 model...")
        detector = AdvancedEmotionDetector(model_type="wav2vec2")
        print("✅ Wav2vec2 detector initialized")
        
        if len(sys.argv) > 1:
            audio_path = sys.argv[1]
            result = detect_emotion_from_file(audio_path, model_type="wav2vec2")
            
            print(f"\n😊 Emotion: {result['emotion'].capitalize()}")
            print(f"   Confidence: {result['confidence']:.2%}")
        
    except Exception as e:
        print(f"❌ Error with wav2vec2: {e}")
    
    if len(sys.argv) <= 1:
        print("\n💡 Usage: python advanced_emotion_detection.py <audio_file>")
