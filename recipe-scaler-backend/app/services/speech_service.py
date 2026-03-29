"""
Speech-to-Text service
Handles transcribing audio using Faster-Whisper model
"""

import logging
import os
from typing import Optional

try:
    from faster_whisper import WhisperModel
except ImportError:
    WhisperModel = None

logger = logging.getLogger(__name__)


class SpeechService:
    """Service for transcribing audio to text using Faster-Whisper"""

    # Whisper model configuration
    MODEL_NAME = "base"  # Options: tiny, base, small, medium, large
    DEVICE = "auto"  # Auto-detect GPU/CPU
    COMPUTE_TYPE = "default"  # Options: default, float16, int8
    _model_instance = None

    @staticmethod
    def get_model():
        """
        Get Whisper model instance (lazy loading)
        
        Returns:
            WhisperModel instance
            
        Raises:
            ImportError: If faster-whisper is not installed
        """
        if WhisperModel is None:
            logger.error("faster-whisper is not installed. Install with: pip install faster-whisper")
            raise ImportError("faster-whisper is required for speech transcription. Install with: pip install faster-whisper")

        if SpeechService._model_instance is None:
            logger.info(f"Loading Whisper model: {SpeechService.MODEL_NAME}")
            try:
                SpeechService._model_instance = WhisperModel(
                    SpeechService.MODEL_NAME,
                    device=SpeechService.DEVICE,
                    compute_type=SpeechService.COMPUTE_TYPE,
                )
                logger.info("Whisper model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load Whisper model: {str(e)}")
                raise

        return SpeechService._model_instance

    @staticmethod
    def transcribe_audio(audio_path: str) -> str:
        """
        Transcribe audio file to text using Faster-Whisper
        
        Args:
            audio_path: Path to audio file (supports WAV, MP3, etc.)
            
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

            # Get model
            model = SpeechService.get_model()

            # Transcribe audio
            logger.debug("Whisper transcription in progress...")
            segments, info = model.transcribe(
                audio_path,
                beam_size=5,
                best_of=5,
                temperature=0.0,  # Greedy decoding for consistency
                condition_on_previous_text=False,  # Disable contextual conditioning for better accuracy
                vad_filter=True,               # Use VAD filter to ignore silence
                vad_parameters=dict(min_silence_duration_ms=500), # Strip out 500ms silences
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
        Unload the Whisper model to free memory
        """
        if SpeechService._model_instance is not None:
            try:
                # Delete the model instance
                del SpeechService._model_instance
                SpeechService._model_instance = None
                logger.info("Whisper model unloaded")
            except Exception as e:
                logger.error(f"Error unloading model: {str(e)}")
