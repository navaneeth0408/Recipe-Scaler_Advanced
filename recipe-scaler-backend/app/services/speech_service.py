"""
Speech-to-Text service
Handles transcribing audio using Faster-Whisper model
"""

import logging
import os
from typing import Optional

# This will be loaded lazily to speed up backend startup
WhisperModel = None

logger = logging.getLogger(__name__)


class SpeechService:
    """Service for transcribing audio to text using Faster-Whisper"""

    # Whisper model configuration
    MODEL_NAME = "base"  # Options: tiny, base, small, medium, large
    DEVICE = "cpu"  # Force CPU for better stability on low-mem machines, or use "auto"
    COMPUTE_TYPE = "int8"  # Optimized for CPU RAM usage
    _models = {}  # Cache for multiple model sizes

    @staticmethod
    def get_model(model_name: str = "base"):
        """
        Get Whisper model instance (lazy loading)
        
        Args:
            model_name: The Whisper model size (e.g. base, small, medium)
            
        Returns:
            WhisperModel instance
            
        Raises:
            ImportError: If faster-whisper is not installed
        """
        global WhisperModel
        if WhisperModel is None:
            logger.info("Lazy importing 'faster_whisper' library...")
            try:
                from faster_whisper import WhisperModel
            except ImportError:
                logger.error("faster-whisper is not installed. Install with: pip install faster-whisper")
                raise ImportError("faster-whisper is required for speech transcription. Install with: pip install faster-whisper")

        if model_name not in SpeechService._models:
            logger.info(f"Loading Whisper model: {model_name}")
            try:
                SpeechService._models[model_name] = WhisperModel(
                    model_name,
                    device=SpeechService.DEVICE,
                    compute_type=SpeechService.COMPUTE_TYPE,
                )
                logger.info(f"Whisper model '{model_name}' loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load Whisper model '{model_name}': {str(e)}")
                if model_name != "base":
                    logger.info("Falling back to 'base' model")
                    return SpeechService.get_model("base")
                raise

        return SpeechService._models[model_name]

    @staticmethod
    def detect_language_from_audio(audio_path: str) -> str:
        """
        Detect language by transcribing only the first 30 seconds of audio.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Language code (e.g., 'en', 'ml')
        """
        if not os.path.exists(audio_path):
            logger.error(f"Audio file not found for language detection: {audio_path}")
            return "en" # Fallback
            
        try:
            logger.info(f"Detecting language from audio: {audio_path}")
            model = SpeechService.get_model("base")
            # Rapid detection with beam_size=1 and 30s chunk
            segments, info = model.transcribe(
                audio_path, 
                beam_size=1, 
                clip_timestamps="0,30"
            )
            detected_lang = info.language
            logger.info(f"Language detected: {detected_lang}")
            return detected_lang
        except Exception as e:
            logger.error(f"Language detection failed: {str(e)}", exc_info=True)
            return "en" # Safely fallback


    @staticmethod
    def transcribe_audio(audio_path: str, language: Optional[str] = None) -> str:
        """
        Transcribe audio file to text using Faster-Whisper
        
        Args:
            audio_path: Path to audio file (supports WAV, MP3, etc.)
            language: Target language code ('en', 'ml')
            
        Returns:
            Transcribed text
            
        Raises:
            ValueError: If transcription fails
            FileNotFoundError: If audio file not found
        """
        if not os.path.exists(audio_path):
            logger.error(f"Audio file not found: {audio_path}")
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        try:
            logger.info(f"Starting transcription for: {audio_path}")

            # Get model - use 'small' for Malayalam to improve accuracy
            model_name = "small" if language == "ml" else "base"
            model = SpeechService.get_model(model_name)

            # Transcribe audio
            beam_size = 10 if language == "ml" else 5
            vad_filter = False if language == "ml" else True
            
            logger.debug(f"Whisper transcription in progress (lang={language}, beam={beam_size}, vad={vad_filter})...")
            
            kwargs = {}
            if language:
                kwargs["language"] = language
                
            vad_parameters = dict(min_silence_duration_ms=500) if vad_filter else None
            
            segments, info = model.transcribe(
                audio_path,
                beam_size=beam_size,
                best_of=5,
                temperature=0.0,  # Greedy decoding for consistency
                condition_on_previous_text=False,  # Disable contextual conditioning for better accuracy
                vad_filter=vad_filter,
                vad_parameters=vad_parameters,
                **kwargs
            )

            logger.debug(f"Transcription completed. Language: {info.language}, Duration: {info.duration}s")

            # Combine all segments into full transcript
            transcript_parts = []
            segment_count = 0

            for segment in segments:
                text = segment.text.strip()
                if text:
                    transcript_parts.append(text)
                    segment_count += 1
                    logger.debug(f"Segment {segment_count}: {text[:100]}...")

            # Join all segments
            full_transcript = " ".join(transcript_parts)

            if not full_transcript:
                logger.warning("No speech detected in audio")
                return ""

            logger.info(f"Successfully transcribed {segment_count} segments into {len(full_transcript)} characters")
            return full_transcript

        except ValueError as ve:
            logger.error(f"Transcription error: {str(ve)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during transcription: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to transcribe audio: {str(e)}")

    @staticmethod
    def unload_model():
        """
        Unload the Whisper models to free memory
        """
        if SpeechService._models:
            try:
                # Delete the model instances
                SpeechService._models.clear()
                logger.info("Whisper models unloaded")
            except Exception as e:
                logger.error(f"Error unloading models: {str(e)}")
