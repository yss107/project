#!/usr/bin/env python3
"""
Video Processing with Subtitle Overlay
Supports video file transcription and subtitle overlay
"""

import numpy as np
import os
from typing import List, Dict, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')


class VideoProcessor:
    """
    Process video files with speech recognition and subtitle overlay
    """
    
    def __init__(
        self,
        whisper_model: Optional[object] = None,
        sample_rate: int = 16000
    ):
        """
        Initialize video processor
        
        Args:
            whisper_model: Pre-loaded Whisper model instance
            sample_rate: Audio sample rate
        """
        self.whisper_model = whisper_model
        self.sample_rate = sample_rate
    
    def extract_audio(
        self,
        video_path: str,
        output_audio_path: Optional[str] = None
    ) -> str:
        """
        Extract audio from video file
        
        Args:
            video_path: Path to video file
            output_audio_path: Path for output audio file (auto-generated if None)
            
        Returns:
            Path to extracted audio file
        """
        try:
            import ffmpeg
            
            if output_audio_path is None:
                base_name = os.path.splitext(video_path)[0]
                output_audio_path = f"{base_name}_audio.wav"
            
            print(f"🎬 Extracting audio from video: {video_path}")
            
            # Extract audio using ffmpeg
            stream = ffmpeg.input(video_path)
            stream = ffmpeg.output(
                stream,
                output_audio_path,
                acodec='pcm_s16le',
                ac=1,  # mono
                ar=str(self.sample_rate)
            )
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            print(f"✅ Audio extracted to: {output_audio_path}")
            return output_audio_path
            
        except ImportError:
            print("⚠️ ffmpeg-python not available. Trying moviepy...")
            return self._extract_audio_moviepy(video_path, output_audio_path)
        except Exception as e:
            print(f"⚠️ Error extracting audio with ffmpeg: {e}")
            return self._extract_audio_moviepy(video_path, output_audio_path)
    
    def _extract_audio_moviepy(
        self,
        video_path: str,
        output_audio_path: Optional[str]
    ) -> str:
        """Extract audio using moviepy as fallback"""
        try:
            from moviepy.editor import VideoFileClip
            
            if output_audio_path is None:
                base_name = os.path.splitext(video_path)[0]
                output_audio_path = f"{base_name}_audio.wav"
            
            print(f"🎬 Extracting audio with moviepy: {video_path}")
            
            video = VideoFileClip(video_path)
            audio = video.audio
            audio.write_audiofile(output_audio_path, fps=self.sample_rate)
            video.close()
            
            print(f"✅ Audio extracted to: {output_audio_path}")
            return output_audio_path
            
        except ImportError as e:
            raise ImportError(
                "Neither ffmpeg-python nor moviepy available. "
                "Install with: pip install ffmpeg-python moviepy"
            ) from e
    
    def transcribe_video(
        self,
        video_path: str,
        target_languages: Optional[List[str]] = None
    ) -> Dict:
        """
        Transcribe video file
        
        Args:
            video_path: Path to video file
            target_languages: List of target languages for translation
            
        Returns:
            Dictionary with transcription and timing information
        """
        if self.whisper_model is None:
            raise RuntimeError("Whisper model not provided")
        
        # Extract audio
        audio_path = self.extract_audio(video_path)
        
        try:
            print(f"🎤 Transcribing audio...")
            
            # Transcribe with Whisper
            result = self.whisper_model.transcribe(
                audio_path,
                task="transcribe",
                word_timestamps=True
            )
            
            print(f"✅ Transcription complete")
            
            # Clean up audio file
            try:
                os.unlink(audio_path)
            except:
                pass
            
            return result
            
        except Exception as e:
            # Clean up audio file on error
            try:
                os.unlink(audio_path)
            except:
                pass
            raise e
    
    def create_subtitle_file(
        self,
        transcription_data: Dict,
        output_path: str,
        format: str = "srt",
        target_language: Optional[str] = None,
        translator: Optional[object] = None
    ) -> str:
        """
        Create subtitle file from transcription
        
        Args:
            transcription_data: Whisper transcription result
            output_path: Path for output subtitle file
            format: Subtitle format ('srt' or 'vtt')
            target_language: Target language for translation
            translator: Translator object for translation
            
        Returns:
            Path to created subtitle file
        """
        print(f"📝 Creating {format.upper()} subtitle file...")
        
        # Get segments from transcription
        segments = transcription_data.get("segments", [])
        
        if format.lower() == "srt":
            content = self._generate_srt(segments, target_language, translator)
        elif format.lower() == "vtt":
            content = self._generate_vtt(segments, target_language, translator)
        else:
            raise ValueError(f"Unsupported subtitle format: {format}")
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Subtitle file created: {output_path}")
        return output_path
    
    def _generate_srt(
        self,
        segments: List[Dict],
        target_language: Optional[str] = None,
        translator: Optional[object] = None
    ) -> str:
        """Generate SRT subtitle content"""
        srt_lines = []
        
        for i, segment in enumerate(segments, 1):
            start = self._format_timestamp_srt(segment["start"])
            end = self._format_timestamp_srt(segment["end"])
            text = segment["text"].strip()
            
            # Translate if requested
            if target_language and translator:
                try:
                    text = translator.translate(text)
                except:
                    pass  # Keep original if translation fails
            
            srt_lines.append(f"{i}")
            srt_lines.append(f"{start} --> {end}")
            srt_lines.append(text)
            srt_lines.append("")  # Blank line between entries
        
        return "\n".join(srt_lines)
    
    def _generate_vtt(
        self,
        segments: List[Dict],
        target_language: Optional[str] = None,
        translator: Optional[object] = None
    ) -> str:
        """Generate WebVTT subtitle content"""
        vtt_lines = ["WEBVTT", ""]
        
        for segment in segments:
            start = self._format_timestamp_vtt(segment["start"])
            end = self._format_timestamp_vtt(segment["end"])
            text = segment["text"].strip()
            
            # Translate if requested
            if target_language and translator:
                try:
                    text = translator.translate(text)
                except:
                    pass  # Keep original if translation fails
            
            vtt_lines.append(f"{start} --> {end}")
            vtt_lines.append(text)
            vtt_lines.append("")  # Blank line between entries
        
        return "\n".join(vtt_lines)
    
    def _format_timestamp_srt(self, seconds: float) -> str:
        """Format timestamp for SRT format (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def _format_timestamp_vtt(self, seconds: float) -> str:
        """Format timestamp for WebVTT format (HH:MM:SS.mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"
    
    def overlay_subtitles(
        self,
        video_path: str,
        subtitle_path: str,
        output_path: str,
        subtitle_style: Optional[Dict] = None
    ) -> str:
        """
        Overlay subtitles on video
        
        Args:
            video_path: Path to input video
            subtitle_path: Path to subtitle file (SRT or VTT)
            output_path: Path for output video
            subtitle_style: Dictionary with subtitle styling options
            
        Returns:
            Path to output video with subtitles
        """
        try:
            import ffmpeg
            
            print(f"🎬 Overlaying subtitles on video...")
            
            # Default subtitle style
            if subtitle_style is None:
                subtitle_style = {
                    "FontName": "Arial",
                    "FontSize": 24,
                    "PrimaryColour": "&H00FFFFFF",  # White
                    "OutlineColour": "&H00000000",  # Black outline
                    "Outline": 2,
                    "Shadow": 1,
                    "MarginV": 20  # Bottom margin
                }
            
            # Build subtitle filter
            subtitle_filter = f"subtitles={subtitle_path}"
            
            # Add styling if provided
            if subtitle_style:
                style_str = ":force_style='"
                style_parts = []
                for key, value in subtitle_style.items():
                    style_parts.append(f"{key}={value}")
                style_str += ",".join(style_parts) + "'"
                subtitle_filter += style_str
            
            # Overlay subtitles using ffmpeg
            stream = ffmpeg.input(video_path)
            stream = ffmpeg.output(
                stream,
                output_path,
                vf=subtitle_filter,
                acodec='copy'  # Copy audio without re-encoding
            )
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            print(f"✅ Video with subtitles created: {output_path}")
            return output_path
            
        except ImportError:
            print("⚠️ ffmpeg-python not available. Trying moviepy...")
            return self._overlay_subtitles_moviepy(
                video_path, subtitle_path, output_path, subtitle_style
            )
        except Exception as e:
            print(f"⚠️ Error overlaying subtitles with ffmpeg: {e}")
            return self._overlay_subtitles_moviepy(
                video_path, subtitle_path, output_path, subtitle_style
            )
    
    def _overlay_subtitles_moviepy(
        self,
        video_path: str,
        subtitle_path: str,
        output_path: str,
        subtitle_style: Optional[Dict]
    ) -> str:
        """Overlay subtitles using moviepy as fallback"""
        try:
            from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
            
            print(f"🎬 Overlaying subtitles with moviepy...")
            
            # Load video
            video = VideoFileClip(video_path)
            
            # Parse subtitle file
            subtitles = self._parse_subtitle_file(subtitle_path)
            
            # Create text clips for each subtitle
            subtitle_clips = []
            for sub in subtitles:
                txt_clip = TextClip(
                    sub["text"],
                    fontsize=subtitle_style.get("FontSize", 24) if subtitle_style else 24,
                    color='white',
                    font=subtitle_style.get("FontName", "Arial") if subtitle_style else "Arial",
                    stroke_color='black',
                    stroke_width=2
                )
                txt_clip = txt_clip.set_position(('center', 'bottom'))
                txt_clip = txt_clip.set_start(sub["start"])
                txt_clip = txt_clip.set_duration(sub["end"] - sub["start"])
                subtitle_clips.append(txt_clip)
            
            # Composite video with subtitles
            final_video = CompositeVideoClip([video] + subtitle_clips)
            final_video.write_videofile(output_path, codec='libx264', audio_codec='aac')
            
            # Clean up
            video.close()
            final_video.close()
            
            print(f"✅ Video with subtitles created: {output_path}")
            return output_path
            
        except ImportError as e:
            raise ImportError(
                "Neither ffmpeg-python nor moviepy available. "
                "Install with: pip install ffmpeg-python moviepy"
            ) from e
    
    def _parse_subtitle_file(self, subtitle_path: str) -> List[Dict]:
        """Parse SRT or VTT subtitle file"""
        ext = os.path.splitext(subtitle_path)[1].lower()
        
        if ext == ".srt":
            return self._parse_srt(subtitle_path)
        elif ext == ".vtt":
            return self._parse_vtt(subtitle_path)
        else:
            raise ValueError(f"Unsupported subtitle format: {ext}")
    
    def _parse_srt(self, srt_path: str) -> List[Dict]:
        """Parse SRT subtitle file"""
        subtitles = []
        
        with open(srt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split into entries
        entries = content.strip().split('\n\n')
        
        for entry in entries:
            lines = entry.split('\n')
            if len(lines) >= 3:
                # Parse timestamp
                timestamp_line = lines[1]
                start_str, end_str = timestamp_line.split(' --> ')
                start = self._parse_srt_timestamp(start_str)
                end = self._parse_srt_timestamp(end_str)
                
                # Get text
                text = '\n'.join(lines[2:])
                
                subtitles.append({
                    "start": start,
                    "end": end,
                    "text": text
                })
        
        return subtitles
    
    def _parse_vtt(self, vtt_path: str) -> List[Dict]:
        """Parse WebVTT subtitle file"""
        subtitles = []
        
        with open(vtt_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip header and blank lines
            if line == "WEBVTT" or not line:
                i += 1
                continue
            
            # Check if line is timestamp
            if '-->' in line:
                start_str, end_str = line.split(' --> ')
                start = self._parse_vtt_timestamp(start_str)
                end = self._parse_vtt_timestamp(end_str)
                
                # Get text from next lines
                i += 1
                text_lines = []
                while i < len(lines) and lines[i].strip():
                    text_lines.append(lines[i].strip())
                    i += 1
                
                text = '\n'.join(text_lines)
                
                subtitles.append({
                    "start": start,
                    "end": end,
                    "text": text
                })
            else:
                i += 1
        
        return subtitles
    
    def _parse_srt_timestamp(self, timestamp: str) -> float:
        """Parse SRT timestamp (HH:MM:SS,mmm) to seconds"""
        time_part, millis = timestamp.strip().split(',')
        h, m, s = map(int, time_part.split(':'))
        return h * 3600 + m * 60 + s + int(millis) / 1000
    
    def _parse_vtt_timestamp(self, timestamp: str) -> float:
        """Parse VTT timestamp (HH:MM:SS.mmm) to seconds"""
        parts = timestamp.strip().split(':')
        if len(parts) == 3:
            h, m, s = parts
            s, millis = s.split('.')
            return int(h) * 3600 + int(m) * 60 + int(s) + int(millis) / 1000
        else:
            m, s = parts
            s, millis = s.split('.')
            return int(m) * 60 + int(s) + int(millis) / 1000


def process_video_with_subtitles(
    video_path: str,
    output_path: str,
    whisper_model: object,
    subtitle_format: str = "srt",
    overlay: bool = True
) -> Tuple[str, str]:
    """
    Convenience function to process video with subtitles
    
    Args:
        video_path: Path to input video
        output_path: Path for output video
        whisper_model: Whisper model instance
        subtitle_format: Subtitle format ('srt' or 'vtt')
        overlay: Whether to overlay subtitles on video
        
    Returns:
        Tuple of (subtitle_path, video_with_subtitles_path)
    """
    processor = VideoProcessor(whisper_model=whisper_model)
    
    # Transcribe video
    transcription = processor.transcribe_video(video_path)
    
    # Create subtitle file
    base_name = os.path.splitext(output_path)[0]
    subtitle_path = f"{base_name}.{subtitle_format}"
    processor.create_subtitle_file(transcription, subtitle_path, format=subtitle_format)
    
    # Overlay subtitles if requested
    if overlay:
        video_output = processor.overlay_subtitles(video_path, subtitle_path, output_path)
        return subtitle_path, video_output
    else:
        return subtitle_path, None


if __name__ == "__main__":
    """Test video processing"""
    print("=" * 80)
    print("Video Processing Test")
    print("=" * 80)
    
    import sys
    
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
        
        print(f"\n📹 Processing video: {video_path}")
        
        # Test audio extraction
        processor = VideoProcessor()
        audio_path = processor.extract_audio(video_path)
        
        print(f"✅ Audio extracted: {audio_path}")
        
        # Clean up
        try:
            os.unlink(audio_path)
            print("🧹 Cleaned up temporary audio file")
        except:
            pass
    else:
        print("\n💡 Usage: python video_processor.py <video_file>")
        print("\n✅ Video processing module initialized successfully")
