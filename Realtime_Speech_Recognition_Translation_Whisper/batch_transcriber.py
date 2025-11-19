#!/usr/bin/env python3
"""
Example script for batch audio file transcription and translation
Using OpenAI Whisper Large V3 with W&B integration
"""

import argparse
import os
from pathlib import Path
from typing import Optional

import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from deep_translator import GoogleTranslator
import wandb


class BatchTranscriber:
    """Batch transcription and translation of audio files"""
    
    def __init__(
        self,
        model_id: str = "openai/whisper-large-v3",
        device: str = "auto",
        target_language: Optional[str] = None,
        use_wandb: bool = False
    ):
        """Initialize batch transcriber"""
        self.model_id = model_id
        self.target_language = target_language
        self.use_wandb = use_wandb
        
        # Setup device
        if device == "auto":
            self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        
        self.torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        
        print(f"🚀 Initializing Whisper Large V3 on {self.device}...")
        self._setup_model()
        
        if target_language:
            self._setup_translator()
        
        if use_wandb:
            self._setup_wandb()
    
    def _setup_model(self):
        """Setup Whisper model"""
        print("📥 Loading model...")
        
        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
            self.model_id,
            torch_dtype=self.torch_dtype,
            low_cpu_mem_usage=True,
            use_safetensors=True
        )
        self.model.to(self.device)
        
        self.processor = AutoProcessor.from_pretrained(self.model_id)
        
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
        
        print("✅ Model loaded successfully!")
    
    def _setup_translator(self):
        """Setup translator"""
        try:
            self.translator = GoogleTranslator(target=self.target_language)
            print(f"✅ Translator ready for: {self.target_language}")
        except Exception as e:
            print(f"⚠️ Could not setup translator: {e}")
            self.translator = None
    
    def _setup_wandb(self):
        """Setup W&B"""
        try:
            wandb.init(
                project="whisper-batch-transcription",
                config={
                    "model": self.model_id,
                    "device": self.device,
                    "target_language": self.target_language,
                }
            )
            print("✅ W&B initialized!")
        except Exception as e:
            print(f"⚠️ Could not initialize W&B: {e}")
            self.use_wandb = False
    
    def transcribe_file(self, audio_path: str) -> dict:
        """
        Transcribe an audio file
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Dictionary with transcription results
        """
        print(f"\n🎵 Processing: {audio_path}")
        
        try:
            result = self.pipe(audio_path)
            transcription = result["text"].strip()
            
            output = {
                "file": audio_path,
                "transcription": transcription,
                "translation": None
            }
            
            # Translate if configured
            if self.target_language and self.translator and transcription:
                try:
                    translation = self.translator.translate(transcription)
                    output["translation"] = translation
                except Exception as e:
                    print(f"⚠️ Translation error: {e}")
            
            # Log to W&B
            if self.use_wandb:
                wandb.log({
                    "file": audio_path,
                    "transcription_length": len(transcription),
                    "has_translation": output["translation"] is not None
                })
            
            return output
            
        except Exception as e:
            print(f"❌ Error processing {audio_path}: {e}")
            return {"file": audio_path, "transcription": "", "translation": None, "error": str(e)}
    
    def transcribe_directory(self, directory: str, output_file: Optional[str] = None):
        """
        Transcribe all audio files in a directory
        
        Args:
            directory: Directory containing audio files
            output_file: Optional output file for results
        """
        audio_extensions = {'.wav', '.mp3', '.m4a', '.flac', '.ogg', '.opus'}
        directory_path = Path(directory)
        
        audio_files = [
            str(f) for f in directory_path.iterdir()
            if f.suffix.lower() in audio_extensions
        ]
        
        if not audio_files:
            print(f"⚠️ No audio files found in {directory}")
            return
        
        print(f"\n📁 Found {len(audio_files)} audio files")
        
        results = []
        for audio_file in audio_files:
            result = self.transcribe_file(audio_file)
            results.append(result)
            
            # Display result
            print(f"📝 Transcription: {result['transcription']}")
            if result.get('translation'):
                print(f"🌍 Translation: {result['translation']}")
        
        # Save results if output file specified
        if output_file:
            self._save_results(results, output_file)
        
        if self.use_wandb:
            wandb.finish()
    
    def _save_results(self, results: list, output_file: str):
        """Save results to file"""
        import json
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved to: {output_file}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Batch audio transcription and translation with Whisper Large V3"
    )
    parser.add_argument(
        "input",
        help="Path to audio file or directory"
    )
    parser.add_argument(
        "--target-language",
        "-t",
        help="Target language code for translation (e.g., es, fr, de)",
        default=None
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output JSON file for results",
        default=None
    )
    parser.add_argument(
        "--wandb",
        action="store_true",
        help="Enable Weights & Biases logging"
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*80)
    print("🎯 Batch Audio Transcription with Whisper Large V3")
    print("="*80 + "\n")
    
    transcriber = BatchTranscriber(
        target_language=args.target_language,
        use_wandb=args.wandb
    )
    
    input_path = Path(args.input)
    
    if input_path.is_file():
        result = transcriber.transcribe_file(str(input_path))
        print(f"\n📝 Transcription: {result['transcription']}")
        if result.get('translation'):
            print(f"🌍 Translation: {result['translation']}")
        
        if args.output:
            transcriber._save_results([result], args.output)
    
    elif input_path.is_dir():
        transcriber.transcribe_directory(str(input_path), args.output)
    
    else:
        print(f"❌ Invalid path: {args.input}")
        return 1
    
    print("\n✅ Processing complete!")
    return 0


if __name__ == "__main__":
    exit(main())
