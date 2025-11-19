"""
Configuration file for Whisper Real-time Speech Recognition & Translation
Edit these settings to customize the application behavior
"""

# ============================================================================
# Model Configuration
# ============================================================================

# Whisper model to use
# Options: 
#   - "openai/whisper-tiny" (39M params, fastest)
#   - "openai/whisper-base" (74M params)
#   - "openai/whisper-small" (244M params)
#   - "openai/whisper-medium" (769M params)
#   - "openai/whisper-large-v2" (1.5B params)
#   - "openai/whisper-large-v3" (1.5B params, best quality, recommended)
MODEL_ID = "openai/whisper-large-v3"

# Device to run on
# Options: "auto" (auto-detect), "cuda" (GPU), "cuda:0" (specific GPU), "cpu"
DEVICE = "auto"

# ============================================================================
# Translation Configuration
# ============================================================================

# Target language for translation (ISO 639-1 code)
# Common options:
#   "es" - Spanish      "fr" - French       "de" - German
#   "it" - Italian      "pt" - Portuguese   "ru" - Russian
#   "ja" - Japanese     "zh" - Chinese      "ko" - Korean
#   "ar" - Arabic       "hi" - Hindi        "nl" - Dutch
#
# Set to None to disable translation
TARGET_LANGUAGE = "es"

# ============================================================================
# Audio Configuration
# ============================================================================

# Audio sample rate in Hz
SAMPLE_RATE = 16000

# Duration of audio chunks in seconds
# Smaller = faster response, less context
# Larger = better accuracy, more context
# Recommended: 3-10 seconds
CHUNK_DURATION = 5.0

# Microphone device index
# None = use default microphone
# Run this to see available devices:
#   import sounddevice; print(sounddevice.query_devices())
MICROPHONE_DEVICE_INDEX = None

# ============================================================================
# Weights & Biases Configuration
# ============================================================================

# Enable W&B logging
USE_WANDB = False

# W&B project name
WANDB_PROJECT = "whisper-realtime-translation"

# W&B entity (username or team)
WANDB_ENTITY = None

# ============================================================================
# Processing Configuration
# ============================================================================

# Maximum new tokens to generate
MAX_NEW_TOKENS = 128

# Chunk length for processing (seconds)
PROCESSING_CHUNK_LENGTH = 30

# Batch size for processing
BATCH_SIZE = 16

# Enable timestamps in transcription
RETURN_TIMESTAMPS = True

# ============================================================================
# Display Configuration
# ============================================================================

# Show processing time for each chunk
SHOW_PROCESSING_TIME = True

# Show translation (if enabled)
SHOW_TRANSLATION = True

# Verbose output (more details)
VERBOSE = False

# ============================================================================
# Advanced Configuration
# ============================================================================

# Use safe tensors for model loading
USE_SAFETENSORS = True

# Low CPU memory usage mode
LOW_CPU_MEM_USAGE = True

# Language for transcription (None = auto-detect)
# Set to specific language code to improve accuracy
# Examples: "en" (English), "es" (Spanish), "fr" (French)
TRANSCRIPTION_LANGUAGE = None

# Task type
# Options: "transcribe" or "translate" (Whisper's built-in translation)
TASK = "transcribe"

# ============================================================================
# Noise Handling
# ============================================================================

# Adjust for ambient noise before starting
ADJUST_FOR_AMBIENT_NOISE = True

# Ambient noise adjustment duration (seconds)
AMBIENT_NOISE_DURATION = 1.0

# Energy threshold for voice detection
# None = auto-adjust, Higher = less sensitive, Lower = more sensitive
ENERGY_THRESHOLD = None

# ============================================================================
# File Output Configuration (for batch processing)
# ============================================================================

# Default output format for batch processing
OUTPUT_FORMAT = "json"  # Options: "json", "txt", "csv"

# Save transcriptions to file
SAVE_TRANSCRIPTIONS = False

# Output directory for saved transcriptions
OUTPUT_DIR = "./output"

# ============================================================================
# Logging Configuration
# ============================================================================

# Log level
# Options: "DEBUG", "INFO", "WARNING", "ERROR"
LOG_LEVEL = "INFO"

# Log to file
LOG_TO_FILE = False

# Log file path
LOG_FILE = "./whisper_translator.log"
