#!/usr/bin/env python3
"""
Quick demo script for testing the translation functionality
without requiring the full Whisper model download
"""

def demo_translation():
    """Demo the translation functionality"""
    print("\n" + "="*80)
    print("🌍 Translation Demo (No Model Required)")
    print("="*80 + "\n")
    
    try:
        from deep_translator import GoogleTranslator
        
        # Test sentences
        sentences = [
            "Hello, how are you?",
            "This is a real-time speech recognition system.",
            "The weather is beautiful today.",
            "I love learning new languages.",
        ]
        
        # Target languages
        languages = {
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
            "ja": "Japanese",
        }
        
        print("📝 Original sentences:\n")
        for i, sentence in enumerate(sentences, 1):
            print(f"{i}. {sentence}")
        
        print("\n" + "="*80)
        
        for lang_code, lang_name in languages.items():
            print(f"\n🌍 Translations to {lang_name} ({lang_code}):")
            print("-" * 80)
            
            translator = GoogleTranslator(target=lang_code)
            
            for sentence in sentences:
                try:
                    translation = translator.translate(sentence)
                    print(f"  • {translation}")
                except Exception as e:
                    print(f"  ❌ Error: {e}")
        
        print("\n" + "="*80)
        print("✅ Translation demo complete!")
        print("\nNext steps:")
        print("1. Install all dependencies: pip install -r requirements.txt")
        print("2. Run the full system: python realtime_speech_translator.py")
        print("="*80 + "\n")
        
    except ImportError:
        print("❌ deep-translator not installed")
        print("Install it with: pip install deep-translator")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True


def show_info():
    """Show system information"""
    print("\n" + "="*80)
    print("ℹ️  System Information")
    print("="*80 + "\n")
    
    import sys
    import platform
    
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Processor: {platform.processor()}")
    
    try:
        import torch
        print(f"PyTorch version: {torch.__version__}")
        print(f"CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"CUDA device: {torch.cuda.get_device_name(0)}")
    except ImportError:
        print("PyTorch: Not installed")
    
    try:
        import transformers
        print(f"Transformers version: {transformers.__version__}")
    except ImportError:
        print("Transformers: Not installed")
    
    print("\n" + "="*80 + "\n")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Quick demo of translation functionality"
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Show system information"
    )
    
    args = parser.parse_args()
    
    if args.info:
        show_info()
    else:
        demo_translation()
    
    return 0


if __name__ == "__main__":
    exit(main())
