"""
Route handlers for YouTube metadata extraction
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import uuid
import logging

from app.models.schemas import (
    YouTubeRequest,
    YouTubeResponse,
    YouTubeMetadata,
    Ingredient,
)
from app.services.youtube_service import YouTubeService
from app.services.ingredient_service import IngredientService
from app.services.translation_service import translation_service, Language
from app.database.db import get_db, YouTubeCacheDB

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/youtube", tags=["youtube"])


@router.post("/extract", response_model=YouTubeResponse)
def extract_youtube_data(
    request: YouTubeRequest,
    db: Session = Depends(get_db)
):
    """
    Extract metadata from YouTube video
    
    Can optionally extract ingredients from transcript.
    
    Supports YouTube URL formats:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://m.youtube.com/watch?v=VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    
    Example request:
    ```json
    {
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "extract_ingredients": true
    }
    ```
    
    Returns:
    - 200: Success with metadata and optional ingredients
    - 400: Invalid URL format or malformed request
    - 404: Video not found or unavailable
    - 500: Server error
    """
    try:
        # Validate input
        if not request.url or not isinstance(request.url, str):
            logger.warning("Empty or invalid URL provided")
            raise HTTPException(
                status_code=400,
                detail="URL is required and must be a non-empty string"
            )

        # Validate URL format
        if not YouTubeService.is_valid_youtube_url(request.url):
            logger.warning(f"Invalid YouTube URL format: {request.url}")
            raise HTTPException(
                status_code=400,
                detail="Invalid URL format. Please provide a valid YouTube URL."
            )

        # Extract video ID
        video_id = YouTubeService.extract_video_id(request.url)
        if not video_id:
            logger.warning(f"Could not extract video ID from URL: {request.url}")
            raise HTTPException(
                status_code=400,
                detail="Could not extract video ID from URL. Please check the URL and try again."
            )

        logger.debug(f"Extracted video ID: {video_id} from URL: {request.url}")

        # Check cache first
        cached = db.query(YouTubeCacheDB).filter(
            YouTubeCacheDB.video_id == video_id
        ).first()

        if cached:
            logger.info(f"Using cached metadata for video {video_id}")
            metadata = cached.to_dict()
            ingredients = None

            # Extract ingredients from transcript if requested
            if request.extract_ingredients:
                transcript = YouTubeService.get_youtube_transcript(video_id)
                if transcript:
                    extracted_ings = YouTubeService.extract_ingredients_from_transcript(transcript)
                    ingredients = [
                        Ingredient(
                            name=ing['name'],
                            quantity=ing.get('quantity', 1.0),
                            unit=ing.get('unit', 'whole'),
                        )
                        for ing in extracted_ings
                    ]
                    logger.debug(f"Extracted {len(ingredients or [])} ingredients from cached video transcript")

            return YouTubeResponse(
                metadata=YouTubeMetadata(**metadata),
                ingredients=ingredients,
                success=True,
            )

        # Fetch fresh metadata from YouTube API
        try:
            metadata_dict = YouTubeService.get_youtube_metadata(video_id)
            if 'duration' in metadata_dict and metadata_dict['duration'] is not None:
                metadata_dict['duration'] = str(metadata_dict['duration'])
        except ValueError as ve:
            error_msg = str(ve)
            
            # Return appropriate status codes based on error type
            if "not found" in error_msg.lower():
                logger.warning(f"Video not found: {video_id}")
                raise HTTPException(
                    status_code=404,
                    detail="Video not found. The video may have been deleted or made private."
                )
            elif "invalid" in error_msg.lower():
                logger.warning(f"Invalid video ID: {video_id}")
                raise HTTPException(
                    status_code=400,
                    detail=error_msg
                )
            elif "api key" in error_msg.lower():
                logger.error(f"API key error: {error_msg}")
                raise HTTPException(
                    status_code=500,
                    detail="Server configuration error. Please try again later."
                )
            elif "timeout" in error_msg.lower() or "network" in error_msg.lower():
                logger.warning(f"Network error fetching video {video_id}: {error_msg}")
                raise HTTPException(
                    status_code=500,
                    detail="Network error connecting to YouTube. Please try again later."
                )
            else:
                logger.warning(f"Could not fetch YouTube metadata for {video_id}: {error_msg}")
                raise HTTPException(
                    status_code=500,
                    detail="Could not fetch video metadata. Please check the URL and try again."
                )

        if not metadata_dict:
            logger.error(f"No metadata returned for video: {video_id}")
            raise HTTPException(
                status_code=500,
                detail="Could not fetch video metadata. Please try again."
            )

        # Cache the metadata
        cache_entry = YouTubeCacheDB(
            id=str(uuid.uuid4()),
            video_id=video_id,
            title=metadata_dict.get('title', ''),
            description=metadata_dict.get('description', ''),
            channel_name=metadata_dict.get('channel_name', ''),
            thumbnail_url=metadata_dict.get('thumbnail_url', ''),
            duration=metadata_dict.get('duration'),
            view_count=metadata_dict.get('view_count'),
            upload_date=metadata_dict.get('upload_date'),
            cache_data=metadata_dict,
        )
        db.add(cache_entry)
        db.commit()
        logger.debug(f"Cached metadata for video: {video_id}")

        # Extract ingredients if requested
        ingredients = None
        if request.extract_ingredients:
            transcript = YouTubeService.get_youtube_transcript(video_id)
            if transcript:
                extracted_ings = YouTubeService.extract_ingredients_from_transcript(transcript)
                ingredients = [
                    Ingredient(
                        name=ing['name'],
                        quantity=ing.get('quantity', 1.0),
                        unit=ing.get('unit', 'whole'),
                    )
                    for ing in extracted_ings
                ]
                logger.info(f"Extracted {len(ingredients)} ingredients from video {video_id} transcript")
            else:
                logger.debug(f"No transcript available for video: {video_id}")

        return YouTubeResponse(
            metadata=YouTubeMetadata(**metadata_dict),
            ingredients=ingredients,
            success=True,
        )

    except HTTPException:
        # Re-raise HTTPException to preserve status codes
        raise
    except Exception as e:
        # Log the ACTUAL exception with full traceback for debugging
        logger.error(
            f"[EXTRACT] UNHANDLED EXCEPTION in /extract endpoint: "
            f"{type(e).__name__}: {str(e)}",
            exc_info=True  # This logs the full stack trace
        )
        # Return a 500 error with details for developers
        raise HTTPException(
            status_code=500,
            detail="Server error processing YouTube URL. Check backend logs for details."
        )


@router.get("/metadata")
def get_youtube_metadata(
    url: str,
    db: Session = Depends(get_db)
):
    """
    Get YouTube metadata only (no ingredient extraction)
    
    Query parameter:
    - url: YouTube video URL (required)
    
    Supports YouTube URL formats:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://m.youtube.com/watch?v=VIDEO_ID
    
    Returns:
    - 200: Success with video metadata
    - 400: Invalid URL format or malformed request
    - 404: Video not found or unavailable
    - 500: Server error
    """
    try:
        # Validate input
        if not url or not isinstance(url, str):
            logger.warning("Empty or invalid URL provided to /metadata")
            raise HTTPException(
                status_code=400,
                detail="URL is required and must be a non-empty string"
            )

        # Validate URL format
        if not YouTubeService.is_valid_youtube_url(url):
            logger.warning(f"Invalid YouTube URL format: {url}")
            raise HTTPException(
                status_code=400,
                detail="Invalid URL format. Please provide a valid YouTube URL."
            )

        # Extract video ID
        video_id = YouTubeService.extract_video_id(url)
        if not video_id:
            logger.warning(f"Could not extract video ID from URL: {url}")
            raise HTTPException(
                status_code=400,
                detail="Could not extract video ID from URL. Please check the URL and try again."
            )

        logger.debug(f"Fetching metadata for video: {video_id}")

        # Check cache first
        cached = db.query(YouTubeCacheDB).filter(
            YouTubeCacheDB.video_id == video_id
        ).first()

        if cached:
            logger.info(f"Using cached metadata for video: {video_id}")
            return {
                'metadata': cached.to_dict(),
                'cached': True,
                'success': True,
            }

        # Fetch fresh metadata
        try:
            metadata_dict = YouTubeService.get_youtube_metadata(video_id)
            if 'duration' in metadata_dict and metadata_dict['duration'] is not None:
                metadata_dict['duration'] = str(metadata_dict['duration'])
        except ValueError as ve:
            error_msg = str(ve)
            
            # Return appropriate status codes based on error type
            if "not found" in error_msg.lower():
                logger.warning(f"Video not found: {video_id}")
                raise HTTPException(
                    status_code=404,
                    detail="Video not found. The video may have been deleted or made private."
                )
            elif "invalid" in error_msg.lower():
                logger.warning(f"Invalid video ID: {video_id}")
                raise HTTPException(status_code=400, detail=error_msg)
            elif "api key" in error_msg.lower():
                logger.error(f"API key error")
                raise HTTPException(
                    status_code=500,
                    detail="Server configuration error. Please try again later."
                )
            else:
                logger.warning(f"Could not fetch metadata for {video_id}: {error_msg}")
                raise HTTPException(status_code=500, detail=error_msg)

        if not metadata_dict:
            logger.error(f"No metadata returned for video: {video_id}")
            raise HTTPException(
                status_code=500,
                detail="Could not fetch video metadata. Please try again."
            )

        # Cache the metadata
        cache_entry = YouTubeCacheDB(
            id=str(uuid.uuid4()),
            video_id=video_id,
            title=metadata_dict.get('title', ''),
            description=metadata_dict.get('description', ''),
            channel_name=metadata_dict.get('channel_name', ''),
            thumbnail_url=metadata_dict.get('thumbnail_url', ''),
            duration=metadata_dict.get('duration'),
            view_count=metadata_dict.get('view_count'),
            upload_date=metadata_dict.get('upload_date'),
            cache_data=metadata_dict,
        )
        db.add(cache_entry)
        db.commit()
        logger.debug(f"Cached metadata for video: {video_id}")

        return {
            'metadata': metadata_dict,
            'cached': False,
            'success': True,
        }

    except HTTPException:
        # Re-raise HTTPException to preserve status codes
        raise
    except Exception as e:
        # Log the ACTUAL exception with full traceback for debugging
        logger.error(
            f"[METADATA] UNHANDLED EXCEPTION in /metadata endpoint: "
            f"{type(e).__name__}: {str(e)}",
            exc_info=True  # This logs the full stack trace
        )
        # Return a 500 error with details for developers
        raise HTTPException(
            status_code=500,
            detail="Server error fetching metadata. Check backend logs for details."
        )
def get_youtube_transcript(
    url: str,
    db: Session = Depends(get_db)
):
    """
    Get YouTube video transcript
    
    Query parameter:
    - url: YouTube video URL (required)
    
    Returns:
    - 200: Success with transcript text
    - 400: Invalid URL format or malformed request
    - 404: Video not found or no transcript available
    - 500: Server error
    
    Note: Transcripts are only available for videos that have captions enabled.
    """
    try:
        # Validate input
        if not url or not isinstance(url, str):
            logger.warning("Empty or invalid URL provided to /transcript")
            raise HTTPException(
                status_code=400,
                detail="URL is required and must be a non-empty string"
            )

        # Validate URL format
        if not YouTubeService.is_valid_youtube_url(url):
            logger.warning(f"Invalid YouTube URL format: {url}")
            raise HTTPException(
                status_code=400,
                detail="Invalid URL format. Please provide a valid YouTube URL."
            )

        # Extract video ID
        video_id = YouTubeService.extract_video_id(url)
        if not video_id:
            logger.warning(f"Could not extract video ID from URL: {url}")
            raise HTTPException(
                status_code=400,
                detail="Could not extract video ID from URL. Please check the URL and try again."
            )

        logger.debug(f"Fetching transcript for video: {video_id}")

        # Try to fetch transcript
        transcript = YouTubeService.get_youtube_transcript(video_id)
        if not transcript:
            logger.warning(f"No transcript available for video: {video_id}")
            raise HTTPException(
                status_code=404,
                detail="No transcript available for this video. The video may not have captions enabled."
            )

        logger.info(f"Successfully fetched transcript for video: {video_id}")
        return {
            'video_id': video_id,
            'transcript': transcript,
            'success': True,
        }

    except HTTPException:
        # Re-raise HTTPException to preserve status codes
        raise
    except Exception as e:
        # Log the ACTUAL exception with full traceback for debugging
        logger.error(
            f"[TRANSCRIPT] UNHANDLED EXCEPTION in /transcript endpoint: "
            f"{type(e).__name__}: {str(e)}",
            exc_info=True  # This logs the full stack trace
        )
        # Return a 500 error with details for developers
        raise HTTPException(
            status_code=500,
            detail="Server error fetching transcript. Check backend logs for details."
        )


# ============================================================================
# AUDIO EXTRACTION ENDPOINT
# ============================================================================

from app.models.schemas import AudioExtractionRequest, AudioExtractionResponse

@router.post("/extract-audio-ingredients")
async def extract_audio_ingredients(
    request: AudioExtractionRequest,
    db: Session = Depends(get_db)
):
    """
    Extract ingredients from YouTube video audio using speech-to-text
    
    When a video has no transcript or description available, this endpoint:
    1. Downloads audio from the YouTube video
    2. Converts speech to text using Whisper
    3. Filters for ingredient-related sentences
    4. Extracts structured ingredients
    5. Caches the transcript for future use
    
    Request body:
    ```json
    {
        "youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID"
    }
    ```
    
    Returns:
    - video_id: YouTube video ID
    - video_title: Video title
    - transcript: Full transcribed speech
    - ingredients: Extracted ingredient list
    - extraction_method: "audio"
    - success: True/False
    
    Status codes:
    - 200: Success
    - 400: Invalid URL or request
    - 404: Video not found
    - 500: Server error (audio download, transcription, etc.)
    """
    from app.models.schemas import AudioExtractionRequest, AudioExtractionResponse
    from app.services.audio_service import AudioService
    from app.services.speech_service import SpeechService
    from app.services.ingredient_filter_service import filter_ingredient_sentences
    from app.database.db import YouTubeTranscriptDB
    import uuid
    
    try:
        # Fallback for direct schema usage
        audio_request = request
        
        youtube_url = audio_request.youtube_url or audio_request.url or getattr(audio_request, 'videoUrl', None)
        
        logger.info(f"[AUDIO_EXTRACTION] Processing YouTube URL: {youtube_url}")
        
        # Validate URL
        if not youtube_url or not isinstance(youtube_url, str):
            logger.warning("[AUDIO_EXTRACTION] Invalid URL provided")
            return {"error": "Audio extraction failed", "details": "Invalid YouTube URL"}
        
        # Validate URL format
        if not YouTubeService.is_valid_youtube_url(youtube_url):
            logger.warning(f"[AUDIO_EXTRACTION] Invalid YouTube URL format: {youtube_url}")
            return {"error": "Audio extraction failed", "details": "Invalid YouTube URL format"}
        
        # Extract video ID
        video_id = YouTubeService.extract_video_id(youtube_url)
        if not video_id:
            logger.warning(f"[AUDIO_EXTRACTION] Could not extract video ID from: {youtube_url}")
            return {"error": "Audio extraction failed", "details": "Could not extract video ID from URL"}
        
        logger.info(f"[AUDIO_EXTRACTION] Extracted video ID: {video_id}")
        
        # Check if transcript is already cached
        cached_transcript = db.query(YouTubeTranscriptDB).filter(
            YouTubeTranscriptDB.video_id == video_id
        ).first()
        
        transcript = None
        video_title = None
        detected_lang = None
        
        if cached_transcript:
            logger.info(f"[AUDIO_EXTRACTION] Using cached transcript for video: {video_id}")
            transcript = cached_transcript.transcript
            video_title = cached_transcript.title
            detected_lang = cached_transcript.language
        else:
            # Get video metadata first
            logger.info(f"[AUDIO_EXTRACTION] Fetching video metadata for: {video_id}")
            try:
                metadata = YouTubeService.get_youtube_metadata(video_id)
                video_title = metadata.get('title', 'Unknown')
                logger.info(f"[AUDIO_EXTRACTION] Got video title: {video_title}")
            except Exception as e:
                logger.warning(f"[AUDIO_EXTRACTION] Could not fetch metadata: {str(e)}")
                video_title = "Unknown"
            
            # Attempt subtitle-first logic
            logger.info("[AUDIO_EXTRACTION] Checking for native Malayalam subtitles...")
            transcript = AudioService.extract_subtitles(youtube_url, langs=['ml'])
            
            if transcript:
                logger.info("[AUDIO_EXTRACTION] Found subtitle track natively! Skipping full audio download.")
                detected_lang = Language.MALAYALAM.value
            else:
                logger.info("[AUDIO_EXTRACTION] No subtitles found, proceeding to audio extraction.")
                # Download audio from YouTube
                logger.info(f"[AUDIO_EXTRACTION] Downloading audio from YouTube video: {video_id}")
                try:
                    audio_path = AudioService.download_youtube_audio(youtube_url)
                    logger.info("Audio downloaded")
                    logger.info(f"[AUDIO_EXTRACTION] Audio downloaded to: {audio_path}")
                except Exception as e:
                    logger.error(f"[AUDIO_EXTRACTION] Audio download failed: {str(e)}")
                    return {"error": "Audio extraction failed", "details": f"Failed to download video audio: {str(e)}"}
                
                logger.info("[AUDIO_EXTRACTION] Detecting language from audio...")
                detected_lang = SpeechService.detect_language_from_audio(audio_path)
                logger.info(f"[AUDIO_EXTRACTION] Detected language from audio: {detected_lang}")
                
                # Transcribe audio using Whisper
                logger.info("Transcription started")
                logger.info(f"[AUDIO_EXTRACTION] Starting speech-to-text transcription with lang={detected_lang}")
                try:
                    transcript = SpeechService.transcribe_audio(audio_path, language=detected_lang)
                    logger.info(f"Transcript length: {len(transcript)}")
                    logger.info(f"[AUDIO_EXTRACTION] Transcription completed, {len(transcript)} characters")
                except Exception as e:
                    logger.error(f"[AUDIO_EXTRACTION] Transcription failed: {str(e)}")
                    # Clean up audio file
                    AudioService.cleanup_audio_file(audio_path)
                    return {"error": "Audio extraction failed", "details": f"Unable to transcribe video audio: {str(e)}"}
                finally:
                    # Clean up audio file
                    AudioService.cleanup_audio_file(audio_path)
            
            # Cache the transcript
            logger.info(f"[AUDIO_EXTRACTION] Caching transcript for video: {video_id}")
            try:
                cache_id = str(uuid.uuid4())
                transcript_cache = YouTubeTranscriptDB(
                    id=cache_id,
                    video_id=video_id,
                    title=video_title,
                    transcript=transcript,
                    extraction_method="audio",
                    language=detected_lang
                )
                db.add(transcript_cache)
                db.commit()
                logger.info(f"[AUDIO_EXTRACTION] Transcript cached successfully")
            except Exception as e:
                logger.warning(f"[AUDIO_EXTRACTION] Failed to cache transcript: {str(e)}")
                db.rollback()
                
        # If the generated transcript is empty, quickly exit without executing NLP code.
        if not transcript:
            logger.info("No text transcribed, returning early.")
            return {"ingredients": [], "source": "audio"}
        
        # Filter transcript for ingredient-related sentences
        logger.info(f"[AUDIO_EXTRACTION] Filtering transcript for ingredient-related content")
        
        # If language is unknown at this point (uncached legacy), try predicting it
        if not detected_lang:
            detected_lang = translation_service.detect_language(transcript)

        # Filter and translate (if 'ml') inside the filter service
        filtered_transcript = filter_ingredient_sentences(transcript, language=detected_lang)
        
        if not filtered_transcript:
            logger.warning(f"[AUDIO_EXTRACTION] No ingredient-related content found in transcript")
            response = AudioExtractionResponse(
                video_id=video_id,
                video_title=video_title,
                transcript=transcript,
                ingredients=[],
                source="audio",
                success=True
            )
            return response.dict()

        # ------------------------------------------------------------------
        # Language handling for downstream parsing
        # ------------------------------------------------------------------
        logger.info(f"[AUDIO_EXTRACTION] Extracted language downstream: {detected_lang}")

        if detected_lang not in (Language.ENGLISH.value, Language.MALAYALAM.value):
            logger.info(
                "[AUDIO_EXTRACTION] Language is not English/Malayalam; "
                "skipping audio-based ingredient extraction."
            )
            response = AudioExtractionResponse(
                video_id=video_id,
                video_title=video_title,
                transcript=transcript,
                ingredients=[],
                source="audio",
                success=True
            )
            return response.dict()

        # Since filter_ingredient_sentences translates Malayalam to English, text_for_extraction is already in English
        text_for_extraction = filtered_transcript
        
        # Extract ingredients from (possibly translated) filtered transcript
        logger.info("Parsing ingredients from transcript")
        logger.info(f"[AUDIO_EXTRACTION] Extracting ingredients from processed transcript")
        try:
            ingredient_service = IngredientService()
            extracted_ingredients = ingredient_service.extract_ingredients(text_for_extraction)
            
            logger.info("Ingredients found")
            logger.info(f"[AUDIO_EXTRACTION] Extracted {len(extracted_ingredients)} ingredients")
            
            if not extracted_ingredients:
                logger.warning(f"[AUDIO_EXTRACTION] No ingredients could be parsed from transcript")
                # Return with empty ingredients list
                extracted_ingredients = []
            
        except Exception as e:
            logger.error(f"[AUDIO_EXTRACTION] Ingredient extraction failed: {str(e)}")
            return {"error": "Audio extraction failed", "details": f"Failed to extract ingredients: {str(e)}"}
        
        # Format response
        response = AudioExtractionResponse(
            video_id=video_id,
            video_title=video_title,
            transcript=transcript,
            ingredients=[
                {
                    "name": ing.get('name', 'unknown'),
                    "quantity": ing.get('quantity', 1.0),
                    "unit": ing.get('unit', 'whole'),
                    "notes": ing.get('notes')
                } for ing in extracted_ingredients
            ],
            source="audio",
            success=True
        )
        
        logger.info(f"[AUDIO_EXTRACTION] Successfully extracted ingredients from audio for video: {video_id}")
        return response.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"[AUDIO_EXTRACTION] UNHANDLED EXCEPTION: {type(e).__name__}: {str(e)}",
            exc_info=True
        )
        return {"error": "Audio extraction failed", "details": str(e)}

