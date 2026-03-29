"""
Pydantic models for Recipe Scaler API
These schemas define the structure of requests and responses
"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
from datetime import datetime


# ============================================================================
# INGREDIENT MODELS
# ============================================================================

class Ingredient(BaseModel):
    """Individual ingredient model"""
    name: str
    quantity: Union[float, str]
    unit: str
    original_quantity: Optional[Union[float, str]] = None
    original_unit: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "flour",
                "quantity": 2.0,
                "unit": "cup",
                "original_quantity": 2.0,
                "original_unit": "cup",
                "notes": "all-purpose"
            }
        }


class IngredientRequest(BaseModel):
    """Request model for extracting ingredients from text"""
    text: str
    serving_size: Optional[int] = 1

    class Config:
        json_schema_extra = {
            "example": {
                "text": "2 cups flour, 1/2 cup sugar, 3 eggs, 1 tsp vanilla extract",
                "serving_size": 4
            }
        }


class ExtractedIngredientsResponse(BaseModel):
    """Response model for extracted ingredients"""
    ingredients: List[Ingredient]
    serving_size: int
    extracted_count: int
    success: bool

    class Config:
        json_schema_extra = {
            "example": {
                "ingredients": [
                    {"name": "flour", "quantity": 2.0, "unit": "cup"},
                    {"name": "sugar", "quantity": 0.5, "unit": "cup"}
                ],
                "serving_size": 4,
                "extracted_count": 2,
                "success": True
            }
        }


# ============================================================================
# YOUTUBE METADATA MODELS
# ============================================================================

class YouTubeMetadata(BaseModel):
    """YouTube video metadata"""
    video_id: str
    title: str
    description: str
    channel_name: str
    thumbnail_url: str
    duration: Optional[str] = None
    view_count: Optional[int] = None
    upload_date: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "video_id": "dQw4w9WgXcQ",
                "title": "Homemade Pizza Recipe",
                "description": "Learn how to make pizza...",
                "channel_name": "Cooking Channel",
                "thumbnail_url": "https://i.ytimg.com/vi/...",
                "duration": "10:30",
                "view_count": 1000000,
                "upload_date": "2024-01-15"
            }
        }


class YouTubeRequest(BaseModel):
    """Request model for fetching YouTube metadata"""
    url: str
    extract_ingredients: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "extract_ingredients": True
            }
        }


class YouTubeResponse(BaseModel):
    """Response model for YouTube data"""
    metadata: YouTubeMetadata
    ingredients: Optional[List[Ingredient]] = None
    success: bool

    class Config:
        json_schema_extra = {
            "example": {
                "metadata": {
                    "video_id": "dQw4w9WgXcQ",
                    "title": "Pizza Recipe",
                    "description": "...",
                    "channel_name": "Cooking",
                    "thumbnail_url": "https://..."
                },
                "ingredients": [],
                "success": True
            }
        }


# ============================================================================
# SCALING MODELS
# ============================================================================

class ScalingRequest(BaseModel):
    """Request model for scaling ingredients"""
    ingredients: List[Ingredient]
    original_servings: Optional[float] = 1.0
    target_servings: Optional[float] = None
    value: Optional[float] = None
    type: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "ingredients": [
                    {"name": "flour", "quantity": 2.0, "unit": "cup"}
                ],
                "original_servings": 4,
                "target_servings": 8
            }
        }


class ScaledIngredientsResponse(BaseModel):
    """Response model for scaled ingredients"""
    original_servings: float
    target_servings: float
    scale_factor: float
    ingredients: List[Ingredient]
    success: bool

    class Config:
        json_schema_extra = {
            "example": {
                "original_servings": 4,
                "target_servings": 8,
                "scale_factor": 2.0,
                "ingredients": [
                    {"name": "flour", "quantity": 4.0, "unit": "cup"}
                ],
                "success": True
            }
        }


# ============================================================================
# RECIPE MODELS
# ============================================================================

class RecipeCreate(BaseModel):
    """Request model for creating a recipe"""
    name: str
    ingredients: List[Ingredient]
    servings: float
    source: str = "manual"  # "youtube" or "manual"
    source_url: Optional[str] = None
    notes: Optional[str] = None
    instructions: Optional[List[str]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Chocolate Chip Cookies",
                "ingredients": [
                    {"name": "flour", "quantity": 2.0, "unit": "cup"}
                ],
                "servings": 24,
                "source": "youtube",
                "source_url": "https://youtube.com/watch?v=..."
            }
        }


class Recipe(RecipeCreate):
    """Complete recipe model"""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "id": "recipe_123",
                "name": "Chocolate Chip Cookies",
                "ingredients": [],
                "servings": 24,
                "source": "youtube",
                "created_at": "2024-01-23T10:30:00",
                "updated_at": "2024-01-23T10:30:00"
            }
        }


class RecipeResponse(BaseModel):
    """Response model for recipe operations"""
    recipe: Recipe
    success: bool
    message: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "recipe": {
                    "id": "recipe_123",
                    "name": "Chocolate Chip Cookies",
                    "ingredients": [],
                    "servings": 24,
                    "source": "youtube",
                    "created_at": "2024-01-23T10:30:00",
                    "updated_at": "2024-01-23T10:30:00"
                },
                "success": True,
                "message": "Recipe created successfully"
            }
        }


class RecipesListResponse(BaseModel):
    """Response model for listing recipes"""
    recipes: List[Recipe]
    total: int
    success: bool

    class Config:
        json_schema_extra = {
            "example": {
                "recipes": [],
                "total": 0,
                "success": True
            }
        }


# ============================================================================
# AUDIO EXTRACTION MODELS
# ============================================================================

class AudioExtractionRequest(BaseModel):
    """Request model for extracting ingredients from YouTube audio"""
    youtube_url: str

    class Config:
        json_schema_extra = {
            "example": {
                "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            }
        }


class AudioExtractionResponse(BaseModel):
    """Response model for audio ingredient extraction"""
    video_id: Optional[str] = None
    video_title: Optional[str] = None
    transcript: Optional[str] = None
    ingredients: List[Ingredient]
    source: str = "audio"
    success: bool = True

    class Config:
        json_schema_extra = {
            "example": {
                "video_id": "dQw4w9WgXcQ",
                "video_title": "Easy Pasta Recipe",
                "transcript": "Today we'll make pasta. Start with 2 cups of flour...",
                "ingredients": [
                    {
                        "name": "flour",
                        "quantity": 2.0,
                        "unit": "cup",
                        "notes": None
                    },
                    {
                        "name": "water",
                        "quantity": 0.5,
                        "unit": "cup",
                        "notes": None
                    }
                ],
                "source": "audio",
                "success": True
            }
        }


# ============================================================================
# ERROR MODELS
# ============================================================================

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    details: Optional[Dict[str, Any]] = None
    success: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Invalid YouTube URL",
                "details": {"url": "invalid format"},
                "success": False
            }
        }


# ============================================================================
# SUBSTITUTION MODELS
# ============================================================================

class Substitute(BaseModel):
    """Detailed substitution suggestion"""
    name: str
    ratio: str
    note: str

    class Config:
        json_schema_extra = {
            "example": {
                "name": "milk powder + water",
                "ratio": "1:1",
                "note": "closest replacement"
            }
        }


class SubstituteRequest(BaseModel):
    """Request model for ingredient substitutions"""
    ingredient: str
    quantity: float
    unit: str

    class Config:
        json_schema_extra = {
            "example": {
                "ingredient": "milk",
                "quantity": 1.0,
                "unit": "cup"
            }
        }


class SubstituteResponse(BaseModel):
    """Response model for detailed ingredient substitutions"""
    substitutes: List[Substitute]

    class Config:
        json_schema_extra = {
            "example": {
                "substitutes": [
                    {
                        "name": "milk powder + water",
                        "ratio": "1:1",
                        "note": "closest replacement"
                    }
                ]
            }
        }
