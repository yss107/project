#!/usr/bin/env python3
"""
Example usage scripts for Whisper Real-time Speech Recognition & Translation
Demonstrates various use cases and configurations
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from realtime_speech_translator import WhisperRealtimeTranslator


def example_1_basic_realtime():
    """Example 1: Basic real-time transcription without translation"""
    print("\n" + "="*80)
    print("Example 1: Basic Real-time Transcription (No Translation)")
    print("="*80 + "\n")
    
    translator = WhisperRealtimeTranslator(
        model_id="openai/whisper-large-v3",
        target_language="es",  # Will transcribe but not translate
        use_wandb=False,
        chunk_duration=5.0
    )
    
    # Record for 30 seconds
    translator.start_recording(duration=30)


def example_2_spanish_translation():
    """Example 2: Real-time transcription with Spanish translation"""
    print("\n" + "="*80)
    print("Example 2: English to Spanish Translation")
    print("="*80 + "\n")
    
    translator = WhisperRealtimeTranslator(
        model_id="openai/whisper-large-v3",
        target_language="es",  # Spanish
        use_wandb=False,
        chunk_duration=5.0
    )
    
    translator.start_recording(duration=60)


def example_3_french_translation():
    """Example 3: Real-time transcription with French translation"""
    print("\n" + "="*80)
    print("Example 3: English to French Translation")
    print("="*80 + "\n")
    
    translator = WhisperRealtimeTranslator(
        model_id="openai/whisper-large-v3",
        target_language="fr",  # French
        use_wandb=False,
        chunk_duration=5.0
    )
    
    translator.start_recording(duration=60)


def example_4_german_translation():
    """Example 4: Real-time transcription with German translation"""
    print("\n" + "="*80)
    print("Example 4: English to German Translation")
    print("="*80 + "\n")
    
    translator = WhisperRealtimeTranslator(
        model_id="openai/whisper-large-v3",
        target_language="de",  # German
        use_wandb=False,
        chunk_duration=5.0
    )
    
    translator.start_recording(duration=60)


def example_5_with_wandb():
    """Example 5: Real-time transcription with W&B logging"""
    print("\n" + "="*80)
    print("Example 5: With Weights & Biases Logging")
    print("="*80 + "\n")
    
    # Check if W&B API key is set
    if not os.getenv("WANDB_API_KEY"):
        print("⚠️ Warning: WANDB_API_KEY not set. Logging will be disabled.")
        print("Set your W&B API key: export WANDB_API_KEY=your_key")
        use_wandb = False
    else:
        use_wandb = True
    
    translator = WhisperRealtimeTranslator(
        model_id="openai/whisper-large-v3",
        target_language="es",
        use_wandb=use_wandb,
        chunk_duration=5.0
    )
    
    translator.start_recording(duration=60)


def example_6_short_chunks():
    """Example 6: Faster response with shorter audio chunks"""
    print("\n" + "="*80)
    print("Example 6: Fast Response Mode (3-second chunks)")
    print("="*80 + "\n")
    
    translator = WhisperRealtimeTranslator(
        model_id="openai/whisper-large-v3",
        target_language="es",
        use_wandb=False,
        chunk_duration=3.0  # Shorter chunks = faster response
    )
    
    translator.start_recording(duration=60)


def example_7_continuous():
    """Example 7: Continuous recording (until manually stopped)"""
    print("\n" + "="*80)
    print("Example 7: Continuous Recording Mode")
    print("Press Ctrl+C to stop")
    print("="*80 + "\n")
    
    translator = WhisperRealtimeTranslator(
        model_id="openai/whisper-large-v3",
        target_language="es",
        use_wandb=False,
        chunk_duration=5.0
    )
    
    # No duration limit - runs until interrupted
    translator.start_recording(duration=None)


def example_8_cpu_mode():
    """Example 8: Force CPU mode (no GPU)"""
    print("\n" + "="*80)
    print("Example 8: CPU-only Mode")
    print("="*80 + "\n")
    
    translator = WhisperRealtimeTranslator(
        model_id="openai/whisper-large-v3",
        device="cpu",  # Force CPU
        target_language="es",
        use_wandb=False,
        chunk_duration=5.0
    )
    
    translator.start_recording(duration=30)


def example_9_multiple_languages():
    """Example 9: Demo multiple target languages in sequence"""
    print("\n" + "="*80)
    print("Example 9: Multiple Language Translations")
    print("="*80 + "\n")
    
    languages = [
        ("es", "Spanish", 20),
        ("fr", "French", 20),
        ("de", "German", 20),
    ]
    
    for lang_code, lang_name, duration in languages:
        print(f"\n🌍 Now translating to {lang_name} ({lang_code})")
        print(f"Speak for {duration} seconds...")
        
        translator = WhisperRealtimeTranslator(
            model_id="openai/whisper-large-v3",
            target_language=lang_code,
            use_wandb=False,
            chunk_duration=5.0
        )
        
        translator.start_recording(duration=duration)
        print(f"\n✅ {lang_name} session complete\n")


def print_menu():
    """Print example menu"""
    print("\n" + "="*80)
    print("🎯 Whisper Real-time Speech Recognition & Translation - Examples")
    print("="*80 + "\n")
    print("Choose an example to run:")
    print("  1. Basic real-time transcription (no translation)")
    print("  2. English to Spanish translation")
    print("  3. English to French translation")
    print("  4. English to German translation")
    print("  5. With Weights & Biases logging")
    print("  6. Fast response mode (3-second chunks)")
    print("  7. Continuous recording (until manually stopped)")
    print("  8. CPU-only mode")
    print("  9. Multiple language translations demo")
    print("  0. Exit")
    print("\n" + "="*80 + "\n")


def main():
    """Main function"""
    examples = {
        "1": example_1_basic_realtime,
        "2": example_2_spanish_translation,
        "3": example_3_french_translation,
        "4": example_4_german_translation,
        "5": example_5_with_wandb,
        "6": example_6_short_chunks,
        "7": example_7_continuous,
        "8": example_8_cpu_mode,
        "9": example_9_multiple_languages,
    }
    
    if len(sys.argv) > 1:
        # Run specific example from command line
        choice = sys.argv[1]
        if choice in examples:
            examples[choice]()
        else:
            print(f"❌ Invalid example number: {choice}")
            print("Valid options: 1-9")
            return 1
    else:
        # Interactive mode
        while True:
            print_menu()
            choice = input("Enter your choice (0-9): ").strip()
            
            if choice == "0":
                print("\n👋 Goodbye!")
                break
            elif choice in examples:
                try:
                    examples[choice]()
                except KeyboardInterrupt:
                    print("\n\n⏹️ Example interrupted by user")
                except Exception as e:
                    print(f"\n❌ Error running example: {e}")
                
                input("\n\nPress Enter to return to menu...")
            else:
                print(f"\n❌ Invalid choice: {choice}")
                input("Press Enter to continue...")
    
    return 0


if __name__ == "__main__":
    exit(main())
