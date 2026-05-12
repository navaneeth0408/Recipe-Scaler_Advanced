"""
YouTube metadata extraction service
Handles fetching video information and extracting ingredients from transcripts
Uses official Google YouTube Data API v3 for reliable metadata extraction
"""

import re
import os
from typing import Optional, Dict, Any
from urllib.parse import urlparse, parse_qs
import logging
import httpx

logger = logging.getLogger(__name__)

# Get YouTube API key from environment
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', '')


class YouTubeService:
    """Service for extracting YouTube metadata and transcripts"""

    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """
        Extract video ID from various YouTube URL formats
        
        Supported formats:
        - https://www.youtube.com/watch?v=dQw4w9WgXcQ
        - https://youtu.be/dQw4w9WgXcQ
        - https://www.youtube.com/embed/dQw4w9WgXcQ
        - https://m.youtube.com/watch?v=dQw4w9WgXcQ
        - URLs with additional query parameters
        
        Returns:
            Video ID string (11 characters) or None if not found
        """
        # Patterns to match video IDs from various YouTube URL formats
        patterns = [
            # Standard formats and mobile
            r'(?:youtube\.com|youtu\.be|m\.youtube\.com)\/(?:watch\?v=|embed\/|v\/)([a-zA-Z0-9_-]{11})',
            # youtu.be short format with or without query params
            r'youtu\.be\/([a-zA-Z0-9_-]{11})',
            # watch?v= format with query params
            r'[\?&]v=([a-zA-Z0-9_-]{11})',
        ]
        
        # Normalize URL to handle various formats
        url = url.strip()
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                # Validate that it's exactly 11 characters of valid characters
                if re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
                    logger.debug(f"Extracted video ID: {video_id} from URL: {url}")
                    return video_id
        
        logger.warning(f"Could not extract video ID from URL: {url}")
        return None

    @staticmethod
    def get_youtube_metadata(video_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch YouTube metadata using official Google YouTube Data API v3
        
        This is the reliable method that uses your configured API key.
        
        Returns:
            Dictionary with video metadata or None on failure
            
        Raises:
            ValueError: For specific error conditions (private video, not found, etc.)
        """
        logger.debug(f"[YOUTUBE_METADATA] Starting metadata fetch for video_id: {video_id}")
        
        if not YOUTUBE_API_KEY:
            logger.error("[YOUTUBE_METADATA] YouTube API key not configured in environment")
            raise ValueError("API key not configured")
        
        if not video_id or not re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
            logger.warning(f"[YOUTUBE_METADATA] Invalid video ID format: {video_id}")
            raise ValueError("Invalid video ID format")

        try:
            # Call YouTube Data API v3
            url = "https://www.googleapis.com/youtube/v3/videos"
            
            params = {
                'id': video_id,
                'part': 'snippet,contentDetails,statistics',
                'key': YOUTUBE_API_KEY,
            }
            
            logger.debug(f"[YOUTUBE_METADATA] Making API request for video: {video_id}")
            
            with httpx.Client() as client:
                response = client.get(url, params=params, timeout=10.0)
            
            logger.debug(f"[YOUTUBE_METADATA] API response status code: {response.status_code}")
            
            # Handle HTTP errors
            if response.status_code == 403:
                logger.error(f"[YOUTUBE_METADATA] 403 Forbidden - API key issue or quota exceeded")
                raise ValueError("API authentication failed")
            
            if response.status_code == 404:
                logger.warning(f"[YOUTUBE_METADATA] 404 Not Found from YouTube API for video: {video_id}")
                raise ValueError("Video not found")
            
            if response.status_code != 200:
                error_detail = response.text[:500] if response.text else "No details"
                logger.error(f"[YOUTUBE_METADATA] YouTube API error {response.status_code}: {error_detail}")
                raise ValueError(f"API error: {response.status_code}")
            
            # Parse response
            try:
                data = response.json()
                logger.debug(f"[YOUTUBE_METADATA] Successfully parsed JSON response")
            except Exception as json_err:
                logger.error(f"[YOUTUBE_METADATA] Failed to parse API response as JSON: {str(json_err)}")
                raise ValueError("Invalid API response format")
            
            # Check if video was found
            items = data.get('items')
            if not items or len(items) == 0:
                logger.warning(f"[YOUTUBE_METADATA] API returned empty items list for video: {video_id}")
                raise ValueError("Video not found")
            
            logger.debug(f"[YOUTUBE_METADATA] Found {len(items)} items in API response")
            
            try:
                item = items[0]
                snippet = item.get('snippet', {})
                details = item.get('contentDetails', {})
                stats = item.get('statistics', {})
                
                logger.debug(f"[YOUTUBE_METADATA] Extracted snippet, details, stats from response")
                
                # Safely get all fields with defaults
                title = snippet.get('title', 'Unknown Title')
                description = snippet.get('description', '')
                channel_name = snippet.get('channelTitle', 'Unknown Channel')
                
                # Handle thumbnail safely - could be missing
                thumbnails = snippet.get('thumbnails', {})
                thumbnail_url = ''
                if thumbnails:
                    # Try high quality first, then default, then standard
                    thumbnail_url = (thumbnails.get('high', {}).get('url') or
                                   thumbnails.get('default', {}).get('url') or
                                   thumbnails.get('standard', {}).get('url') or
                                   '')
                
                logger.debug(f"[YOUTUBE_METADATA] Thumbnail URL: {thumbnail_url[:50] if thumbnail_url else 'NONE'}")
                
                # Parse duration from ISO 8601 format (PT1H2M3S)
                duration_str = details.get('duration', '')
                logger.debug(f"[YOUTUBE_METADATA] Duration string from API: {duration_str}")
                duration_seconds = YouTubeService._parse_iso8601_duration(duration_str)
                logger.debug(f"[YOUTUBE_METADATA] Parsed duration: {duration_seconds} seconds")
                
                # Safely handle view count
                view_count = 0
                view_count_str = stats.get('viewCount')
                if view_count_str:
                    try:
                        view_count = int(view_count_str)
                    except (ValueError, TypeError):
                        logger.warning(f"[YOUTUBE_METADATA] Could not parse viewCount: {view_count_str}")
                        view_count = 0
                
                upload_date = snippet.get('publishedAt', '')
                
                logger.debug(f"[YOUTUBE_METADATA] All fields successfully extracted")
                
                metadata = {
                    'video_id': video_id,
                    'title': title,
                    'description': description,
                    'channel_name': channel_name,
                    'thumbnail_url': thumbnail_url,
                    'duration': duration_seconds,  # in seconds
                    'view_count': view_count,
                    'upload_date': upload_date,
                }
                
                logger.info(f"[YOUTUBE_METADATA] Successfully fetched metadata for video: {video_id}")
                logger.debug(f"[YOUTUBE_METADATA] Metadata: title='{title}', duration={duration_seconds}s, views={view_count}")
                return metadata
                
            except ValueError as val_err:
                raise val_err
            except KeyError as key_err:
                logger.error(f"[YOUTUBE_METADATA] Missing expected key in API response: {str(key_err)}", exc_info=True)
                raise ValueError("Incomplete API response")
            except Exception as parse_err:
                logger.error(f"[YOUTUBE_METADATA] Error parsing API response structure: {str(parse_err)}", exc_info=True)
                raise ValueError("Could not parse video metadata")
            
        except ValueError as ve:
            # Re-raise ValueError exceptions (known error conditions)
            raise ve
        except httpx.TimeoutException as timeout_err:
            logger.error(f"[YOUTUBE_METADATA] Request timeout fetching metadata for video: {video_id}")
            raise ValueError("Timeout: YouTube API not responding")
        except httpx.RequestError as req_err:
            logger.error(f"[YOUTUBE_METADATA] Network error fetching YouTube metadata: {str(req_err)}")
            raise ValueError("Network error connecting to YouTube")
        except Exception as e:
            logger.error(f"[YOUTUBE_METADATA] UNEXPECTED ERROR: {type(e).__name__}: {str(e)}", exc_info=True)
            raise ValueError("Unexpected error fetching metadata")

    @staticmethod
    def _parse_iso8601_duration(duration_str: str) -> Optional[int]:
        """
        Parse ISO 8601 duration format (PT1H2M3S) to seconds
        
        Examples:
        - PT10M30S → 630 seconds
        - PT1H → 3600 seconds
        - PT45S → 45 seconds
        - PT0S → 0 seconds
        """
        if not duration_str:
            return None
        
        try:
            # Pattern: PT[n]H[n]M[n]S
            match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
            if not match:
                logger.warning(f"Could not parse duration: {duration_str}")
                return None
            
            hours = int(match.group(1) or 0)
            minutes = int(match.group(2) or 0)
            seconds = int(match.group(3) or 0)
            
            total_seconds = hours * 3600 + minutes * 60 + seconds
            return total_seconds
        except Exception as e:
            logger.warning(f"Error parsing duration '{duration_str}': {str(e)}")
            return None

    @staticmethod
    def get_youtube_transcript(video_id: str) -> Optional[str]:
        """
        Fetch and concatenate YouTube transcript/captions
        
        Returns concatenated transcript text for ingredient extraction
        
        Note: This requires captions to be available on the video.
              If no captions are available, returns None.
        """
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
        except ImportError:
            logger.warning("youtube-transcript-api not installed - transcript extraction disabled")
            return None

        try:
            # Try to get transcript in English, with fallback to auto-generated
            transcript = YouTubeTranscriptApi.get_transcript(
                video_id, 
                languages=['en']
            )
            
            # Concatenate all transcript parts
            full_text = ' '.join([item['text'] for item in transcript])
            logger.debug(f"Successfully fetched transcript for video: {video_id}")
            return full_text
        except Exception as e:
            logger.warning(f"Could not fetch transcript for {video_id}: {str(e)}")
            # This is not a critical failure - many videos don't have transcripts
            return None

    @staticmethod
    def extract_ingredients_from_transcript(transcript: str) -> list:
        """
        Extract ingredients from YouTube transcript using strict whitelist from IngredientService.
        
        Args:
            transcript: Full video transcript text
            
        Returns:
            List of extracted ingredients with quantities
        """
        if not transcript:
            return []
            
        from app.services.ingredient_service import IngredientService
        
        try:
            # Re-use the robust, strict ingredient service logic
            extracted = IngredientService.extract_ingredients(transcript)
            
            for ing in extracted:
                ing['extracted'] = True
            
            logger.debug(f"Extracted {len(extracted)} ingredients strictly from transcript")
            return extracted
        except Exception as e:
            logger.error(f"Error extracting ingredients from transcript: {str(e)}")
            return []

    @staticmethod
    def extract_ingredients_from_description(description: str) -> list:
        """
        Extract ingredients from YouTube video description using AI service.
        Descriptions often contain organized ingredient lists.
        """
        if not description:
            return []
            
        from app.services.ai_ingredient_service import ai_ingredient_service
        
        try:
            logger.info("Extracting ingredients from YouTube description using AI")
            ingredients = ai_ingredient_service.extract_and_normalize_ingredients(description)
            return ingredients
        except Exception as e:
            logger.error(f"Error extracting ingredients from description: {str(e)}")
            return []

    @staticmethod
    def is_valid_youtube_url(url: str) -> bool:
        """
        Validate if URL is a valid YouTube URL
        
        Supports:
        - youtube.com/watch?v=...
        - youtu.be/...
        - youtube.com/embed/...
        - m.youtube.com/watch?v=...
        
        Args:
            url: URL string to validate
            
        Returns:
            True if URL appears to be a YouTube URL, False otherwise
        """
        if not url or not isinstance(url, str):
            return False
        
        youtube_patterns = [
            r'youtube\.com/watch\?',
            r'youtu\.be/',
            r'youtube\.com/embed/',
            r'youtube\.com/v/',
            r'm\.youtube\.com/watch\?',
        ]
        
        return any(re.search(pattern, url, re.IGNORECASE) for pattern in youtube_patterns)

