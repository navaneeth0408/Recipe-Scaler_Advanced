"""
Audio download service
Handles downloading audio from YouTube videos using yt-dlp
"""

import os
import logging
import shutil
from typing import Optional
from pathlib import Path

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

logger = logging.getLogger(__name__)


class AudioService:
    """Service for downloading audio from YouTube videos"""

    # Temp directory for storing downloaded audio files
    TEMP_DIR = Path(__file__).parent.parent.parent / "temp"

    @staticmethod
    def ensure_temp_dir():
        """Ensure temp directory exists"""
        AudioService.TEMP_DIR.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured temp directory exists: {AudioService.TEMP_DIR}")

    @staticmethod
    def download_youtube_audio(video_url: str) -> str:
        """
        Download best audio from YouTube video
        
        Args:
            video_url: YouTube video URL
            
        Returns:
            Path to downloaded audio file
            
        Raises:
            ValueError: If download fails
            ImportError: If yt-dlp is not installed
        """
        if yt_dlp is None:
            logger.error("yt-dlp is not installed. Install with: pip install yt-dlp")
            raise ImportError("yt-dlp is required for audio extraction. Install with: pip install yt-dlp")

        # Validate URL
        if not video_url or not isinstance(video_url, str):
            logger.error(f"Invalid video URL: {video_url}")
            raise ValueError("Invalid YouTube URL")

        try:
            import time
            from app.services.youtube_service import YouTubeService
            
            # Ensure temp directory exists
            AudioService.ensure_temp_dir()

            logger.info(f"Starting audio download from: {video_url}")
            
            video_id = YouTubeService.extract_video_id(video_url) or "audio"
            timestamp = int(time.time())
            filename = f"{video_id}_{timestamp}"

            # yt-dlp options for downloading best audio only
            ydl_opts = {
                # Prioritize webm to avoid FixupM4a post-processor which causes [WinError 5] on Windows
                'format': 'bestaudio[ext=webm]/bestaudio/best', 
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',  # Convert to WAV for Whisper
                    'preferredquality': '192',
                }],
                'postprocessor_args': [
                    '-ac', '1',          # Mono audio (1 channel)
                    '-ar', '16000'       # 16 kHz sample rate (optimal for Whisper)
                ],
                'outtmpl': str(AudioService.TEMP_DIR / f"{filename}.%(ext)s"),  # Output template
                'quiet': False,
                'no_warnings': False,
                'socket_timeout': 30,
                'extractor_retries': 3,
                'sleep_interval_requests': 1,
            }

            logger.debug(f"yt-dlp options: {ydl_opts}")

            # Download audio
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.debug(f"Downloading audio for: {video_url}")
                info = ydl.extract_info(video_url, download=True)
                downloaded_id = info.get('id')
                logger.info(f"Successfully downloaded audio for video ID: {downloaded_id}")

            # Find the downloaded file regardless of the codec extension applied
            possible_files = list(AudioService.TEMP_DIR.glob(f"{filename}.*"))
            if not possible_files:
                logger.error(f"Downloaded audio file not found for filename: {filename}")
                raise ValueError("Failed to download audio - file not created")

            audio_path = possible_files[0]
            logger.info(f"Audio file saved to: {audio_path}")
            return str(audio_path)

        except yt_dlp.utils.DownloadError as e:
            logger.error(f"yt-dlp download error: {str(e)}")
            raise ValueError(f"Failed to download video audio: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during audio download: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to download audio: {str(e)}")

    @staticmethod
    def cleanup_audio_file(file_path: str) -> bool:
        """
        Delete audio file after processing
        
        Args:
            file_path: Path to audio file to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            if os.path.exists(file_path):
                import time
                time.sleep(0.5) # Allow Windows file handles from Whisper/FFmpeg to fully release
                os.remove(file_path)
                logger.debug(f"Cleaned up audio file: {file_path}")
                return True
            else:
                logger.warning(f"Audio file not found for cleanup: {file_path}")
                return False
        except PermissionError as e:
            logger.warning(f"File locked, could not clean up {file_path}. It will be cleaned up later: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Failed to clean up audio file {file_path}: {str(e)}")
            return False

    @staticmethod
    def cleanup_all_temp_files() -> int:
        """
        Delete all files in temp directory
        
        Returns:
            Number of files deleted
        """
        try:
            if not AudioService.TEMP_DIR.exists():
                logger.debug("Temp directory does not exist")
                return 0

            deleted_count = 0
            for file in AudioService.TEMP_DIR.glob('*'):
                if file.is_file():
                    try:
                        file.unlink()
                        deleted_count += 1
                        logger.debug(f"Deleted temp file: {file}")
                    except Exception as e:
                        logger.warning(f"Failed to delete {file}: {str(e)}")

            logger.info(f"Cleaned up {deleted_count} temp files")
            return deleted_count
        except Exception as e:
            logger.error(f"Failed to cleanup temp directory: {str(e)}")
            return 0

    @staticmethod
    def extract_subtitles(video_url: str, langs: Optional[list] = None) -> Optional[str]:
        """
        Extract subtitles directly using yt-dlp without downloading full audio.
        Optimized for speed.
        
        Args:
            video_url: URL to the YouTube video
            langs: List of language codes to attempt (e.g. ['ml', 'en'])
            
        Returns:
            Concatenated subtitle text, or None if no matching subtitles exist.
        """
        if yt_dlp is None:
            return None
            
        if langs is None:
            langs = ['ml']
            
        try:
            import time
            import re
            from app.services.youtube_service import YouTubeService
            
            AudioService.ensure_temp_dir()
            video_id = YouTubeService.extract_video_id(video_url) or "subtitle"
            timestamp = int(time.time())
            filename = f"{video_id}_{timestamp}_sub"
            
            ydl_opts = {
                'skip_download': True,      # Do not download video/audio
                'writesubtitles': True,     # Download manual subtitles
                'writeautomaticsub': True,  # Fallback to auto-generated
                'subtitleslangs': langs,    # Try to fetch these languages
                'subtitlesformat': 'vtt',
                'outtmpl': str(AudioService.TEMP_DIR / f"{filename}.%(ext)s"),
                'quiet': True,
                'no_warnings': True,
                'extractor_retries': 3,
                'sleep_interval_requests': 1,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info(f"Attempting to download subtitles for languages: {langs}")
                ydl.extract_info(video_url, download=True)
                
            # Find the downloaded .vtt file (name varies slightly depending on lang and auto vs manual)
            possible_files = list(AudioService.TEMP_DIR.glob(f"{filename}*.vtt"))
            if not possible_files:
                logger.info(f"No .vtt subtitles found for {video_id} in languages: {langs}")
                return None
                
            sub_file = possible_files[0]
            logger.info(f"Found subtitle file: {sub_file.name}")
            
            with open(sub_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            AudioService.cleanup_audio_file(str(sub_file))
            
            # Simple VTT parser: strip timestamps, HTML/WEBVTT tags, and empty lines
            text_lines = []
            for line in content.split('\n'):
                line = line.strip()
                if not line or line == 'WEBVTT' or '-->' in line or line.startswith('Kind:') or line.startswith('Language:'):
                    continue
                # Remove tags like <c>
                clean_line = re.sub(r'<[^>]+>', '', line)
                if clean_line:
                    text_lines.append(clean_line)
                    
            full_text = " ".join(text_lines)
            
            # Deduplicate repeated words (common in auto-generated captions)
            words = full_text.split()
            dedup_words = []
            for w in words:
                if not dedup_words or dedup_words[-1] != w:
                    dedup_words.append(w)
                    
            return " ".join(dedup_words) if dedup_words else full_text
            
        except Exception as e:
            logger.warning(f"Failed to extract subtitles via yt-dlp: {str(e)}")
            return None
