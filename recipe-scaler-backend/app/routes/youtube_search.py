"""
Route handlers for YouTube search functionality
Enhanced search with filtering, ranking, and pagination support
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging
import os
import httpx

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/youtube", tags=["youtube-search"])

# Get YouTube API key from environment
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', '')

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class SearchResult(BaseModel):
    """Individual search result"""
    video_id: str
    title: str
    channel: str
    thumbnail_url: str
    views: Optional[int] = None
    duration_seconds: Optional[int] = None
    published_date: Optional[str] = None
    relevance_score: Optional[float] = None

    class Config:
        json_schema_extra = {
            "example": {
                "video_id": "dQw4w9WgXcQ",
                "title": "Homemade Pizza Recipe",
                "channel": "Cooking Channel",
                "thumbnail_url": "https://i.ytimg.com/vi/...",
                "views": 1000000,
                "duration_seconds": 600,
                "published_date": "2024-01-15",
                "relevance_score": 95.5
            }
        }


class YouTubeSearchRequest(BaseModel):
    """Request model for YouTube search"""
    query: str = Field(..., description="Search query (e.g., 'pasta recipe')")
    category: Optional[str] = Field(default=None, description="Recipe category (e.g., 'pasta', 'chicken')")
    page_token: Optional[str] = Field(default=None, description="Pagination token")
    max_results: int = Field(default=6, description="Max results to return")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "pasta",
                "category": "pasta",
                "page_token": "",
                "max_results": 6
            }
        }


class YouTubeSearchResponse(BaseModel):
    """Response model for YouTube search"""
    results: List[SearchResult]
    next_page_token: Optional[str] = None
    prev_page_token: Optional[str] = None
    total_results: Optional[int] = None
    success: bool

    class Config:
        json_schema_extra = {
            "example": {
                "results": [
                    {
                        "video_id": "dQw4w9WgXcQ",
                        "title": "Pasta Recipe",
                        "channel": "Cooking",
                        "thumbnail_url": "https://...",
                        "views": 100000,
                        "duration_seconds": 600
                    }
                ],
                "next_page_token": "...",
                "prev_page_token": None,
                "total_results": 10000,
                "success": True
            }
        }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def parse_duration_iso8601(duration_str: str) -> int:
    """
    Parse ISO 8601 duration format (PT1H2M3S) to seconds
    
    Examples:
    - PT10M30S -> 630 seconds
    - PT1H -> 3600 seconds
    - PT45S -> 45 seconds
    """
    import re
    
    if not duration_str:
        return 0
    
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
    if not match:
        return 0
    
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    
    return hours * 3600 + minutes * 60 + seconds


def score_search_result(
    item: Dict[str, Any],
    video_detail: Dict[str, Any],
    query: str
) -> float:
    """
    Score a search result based on various factors
    
    Higher score = better match
    """
    score = 0
    
    # Keywords that suggest ingredient list
    ingredient_keywords = [
        'ingredient', 'ingredients', 'recipe', 'cup', 'tablespoon',
        'teaspoon', 'gram', 'oz', 'ounce', 'pound', 'ml', 'liter', 'kg'
    ]
    
    # Check description for ingredient keywords
    description = video_detail.get('description', '').lower()
    title = video_detail.get('title', '').lower()
    
    for keyword in ingredient_keywords:
        if keyword in description:
            score += 5
        if keyword in title:
            score += 10
    
    # Check for ingredient lines (lines with numbers and units)
    lines = description.split('\n')
    potential_ingredient_lines = 0
    
    for line in lines:
        has_numbers = any(char.isdigit() for char in line)
        has_units = any(unit in line.lower() for unit in [
            'cup', 'tbsp', 'tsp', 'tablespoon', 'teaspoon', 'gram', 'g',
            'oz', 'pound', 'lb', 'ml', 'l'
        ])
        
        if has_numbers and has_units:
            potential_ingredient_lines += 1
    
    score += potential_ingredient_lines * 3
    
    # Prefer longer videos (less likely to be shorts)
    duration_seconds = video_detail.get('duration_seconds', 0)
    
    if duration_seconds > 180:  # > 3 minutes
        score += 10
    elif duration_seconds < 60:  # < 1 minute (likely a short)
        score -= 20
    
    # Penalize if it appears to be a short
    if any(indicator in title for indicator in ['#short', '#shorts', 'short video']):
        score -= 50
    
    return score


def filter_search_results(
    search_items: List[Dict[str, Any]],
    video_details: List[Dict[str, Any]],
    query: str,
    max_results: int
) -> List[Dict[str, Any]]:
    """
    Filter, score, and rank search results
    
    Removes shorts and low-quality results, ranks by relevance
    """
    scored_results = []
    
    for item in search_items:
        video_id = item['id']['videoId']
        
        # Find corresponding video detail
        video_detail = None
        for detail in video_details:
            if detail.get('id') == video_id:
                video_detail = detail
                break
        
        if not video_detail:
            continue
        
        # Score this result
        score = score_search_result(item, video_detail, query)
        
        # Skip results with very low scores
        if score < -20:
            continue
        
        # Parse duration
        duration_str = video_detail.get('contentDetails', {}).get('duration', 'PT0S')
        duration_seconds = parse_duration_iso8601(duration_str)
        
        # Create result object
        result = {
            'video_id': video_id,
            'title': item['snippet']['title'],
            'channel': item['snippet']['channelTitle'],
            'thumbnail_url': item['snippet']['thumbnails'].get('high', {}).get('url', ''),
            'views': int(video_detail.get('statistics', {}).get('viewCount', 0)),
            'duration_seconds': duration_seconds,
            'published_date': item['snippet']['publishedAt'][:10],
            'relevance_score': score,
        }
        
        scored_results.append(result)
    
    # Sort by score (descending) and return top results
    scored_results.sort(key=lambda x: x['relevance_score'], reverse=True)
    
    return scored_results[:max_results]


# ============================================================================
# SEARCH ENDPOINT
# ============================================================================

@router.post("/search", response_model=YouTubeSearchResponse)
async def search_youtube(request: YouTubeSearchRequest):
    """
    Search YouTube for recipe videos
    
    Returns filtered, ranked results with:
    - Relevance scoring
    - Shorts filtered out
    - Videos with potential ingredient lists prioritized
    - Pagination support
    
    Example request:
    ```json
    {
        "query": "pasta carbonara",
        "category": "pasta",
        "page_token": "",
        "max_results": 6
    }
    ```
    """
    try:
        if not YOUTUBE_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="YouTube API key not configured. Set YOUTUBE_API_KEY environment variable."
            )
        
        if not request.query or len(request.query.strip()) == 0:
            raise HTTPException(status_code=400, detail="Search query cannot be empty")
        
        # Build search query
        search_term = request.query.strip()
        if request.category:
            search_term += f" {request.category} recipe"
        else:
            search_term += " recipe"
        
        # Add keywords to increase chances of finding videos with ingredients
        search_term += " ingredients"
        
        # Build API URL
        params = {
            'part': 'snippet',
            'type': 'video',
            'videoDefinition': 'high',
            'videoDuration': 'medium',
            'maxResults': '15',
            'q': search_term,
            'key': YOUTUBE_API_KEY
        }
        
        if request.page_token:
            params['pageToken'] = request.page_token
        
        # Make search request
        async with httpx.AsyncClient() as client:
            search_response = await client.get(
                'https://www.googleapis.com/youtube/v3/search',
                params=params
            )
            search_response.raise_for_status()
            search_data = search_response.json()
        
        if not search_data.get('items'):
            return YouTubeSearchResponse(
                results=[],
                next_page_token=None,
                prev_page_token=None,
                success=True
            )
        
        # Get video details (for statistics and content details)
        video_ids = ','.join([item['id']['videoId'] for item in search_data['items']])
        
        async with httpx.AsyncClient() as client:
            details_response = await client.get(
                'https://www.googleapis.com/youtube/v3/videos',
                params={
                    'part': 'statistics,snippet,contentDetails',
                    'id': video_ids,
                    'key': YOUTUBE_API_KEY
                }
            )
            details_response.raise_for_status()
            video_details = details_response.json()['items']
        
        # Filter and rank results
        filtered_results = filter_search_results(
            search_data['items'],
            video_details,
            request.query,
            request.max_results
        )
        
        return YouTubeSearchResponse(
            results=filtered_results,
            next_page_token=search_data.get('nextPageToken'),
            prev_page_token=search_data.get('prevPageToken'),
            total_results=search_data.get('pageInfo', {}).get('totalResults'),
            success=True
        )
    
    except httpx.HTTPError as e:
        logger.error(f"YouTube API error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error communicating with YouTube API: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error searching YouTube: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
