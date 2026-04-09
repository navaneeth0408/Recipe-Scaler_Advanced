"""
Route handlers for AI-powered features
Includes ingredient extraction, substitution, nutrition, chat, and translation endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
import uuid

from app.services.ai_ingredient_service import ai_ingredient_service
from app.services.ai_substitution_service import ai_substitution_service
from app.services.nutrition_service import nutrition_service
from app.services.chat_service import cooking_assistant
from app.services.translation_service import translation_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ai", tags=["ai"])

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ExtractIngredientRequest(BaseModel):
    """Request model for ingredient extraction"""
    text: str = Field(..., description="Raw text containing ingredients")

class ExtractIngredientResponse(BaseModel):
    """Response model for ingredient extraction"""
    ingredients: List[Dict[str, Any]]
    count: int

class SubstituteRequest(BaseModel):
    """Request model for ingredient substitution"""
    ingredient: str = Field(..., description="Ingredient to substitute")
    quantity: float = Field(default=1.0, description="Quantity of ingredient")
    unit: str = Field(default="piece", description="Unit of measurement")
    dietary_preference: Optional[str] = Field(default=None, description="Dietary preference (vegan, gluten_free, etc.)")
    cuisine: Optional[str] = Field(default=None, description="Cuisine type")
    available_ingredients: Optional[List[str]] = Field(default=None, description="List of available ingredients")

class SubstituteResponse(BaseModel):
    """Response model for substitutions"""
    ingredient: str
    substitutions: List[Dict[str, Any]]

class NutritionRequest(BaseModel):
    """Request model for nutrition analysis"""
    ingredients: List[Dict[str, Any]] = Field(..., description="List of ingredients with quantity and unit")
    servings: int = Field(default=1, description="Number of servings")
    scale_factor: Optional[float] = Field(default=None, description="Factor to scale nutrition (e.g., 0.5 for half)")

class NutritionResponse(BaseModel):
    """Response model for nutrition analysis"""
    total: Dict[str, float]
    per_serving: Dict[str, float]
    ingredients: List[Dict[str, Any]]
    servings: int

class ChatMessage(BaseModel):
    """Request model for chat"""
    session_id: Optional[str] = Field(default=None, description="Session ID for conversation context")
    message: str = Field(..., description="User message")
    recipe_context: Optional[Dict[str, Any]] = Field(default=None, description="Recipe context for assistance")
    dietary_restrictions: Optional[List[str]] = Field(default=None, description="User's dietary restrictions")

class ChatResponse(BaseModel):
    """Response model for chat"""
    session_id: str
    user_message: str
    assistant_response: str
    conversation_history: List[Dict[str, str]]

class TranslateRequest(BaseModel):
    """Request model for translation"""
    text: Optional[str] = Field(default=None, description="Single text to translate")
    texts: Optional[List[str]] = Field(default=None, description="Multiple texts to translate")
    ingredients: Optional[List[Dict[str, Any]]] = Field(default=None, description="Ingredients to translate")
    recipe: Optional[Dict[str, Any]] = Field(default=None, description="Complete recipe to translate")
    target_language: str = Field(..., description="Target language code (en, hi, ml, ta)")

class TranslateResponse(BaseModel):
    """Response model for translation"""
    source_language: str
    target_language: str
    original: Any
    translated: Any

# ============================================================================
# ENDPOINT 1: AI-BASED INGREDIENT EXTRACTION
# ============================================================================

@router.post("/extract", response_model=ExtractIngredientResponse)
async def extract_ingredients(request: ExtractIngredientRequest):
    """
    Extract and normalize ingredients from raw text
    
    Uses transformer-based NLP to:
    - Identify ingredients
    - Predict missing quantities
    - Normalize units
    - Handle vague phrases like "pinch", "handful"
    """
    try:
        if not request.text or len(request.text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        ingredients = ai_ingredient_service.extract_and_normalize_ingredients(request.text)
        
        return ExtractIngredientResponse(
            ingredients=ingredients,
            count=len(ingredients)
        )
    
    except Exception as e:
        logger.error(f"Error extracting ingredients: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ENDPOINT 2: SMART INGREDIENT SUBSTITUTION
# ============================================================================

@router.post("/substitute", response_model=SubstituteResponse)
async def suggest_substitutions(request: SubstituteRequest):
    """
    Suggest ingredient substitutions based on:
    - Dietary preferences (vegan, gluten-free, keto, etc.)
    - Ingredient availability
    - Cuisine type
    
    Returns alternatives with adjusted quantities and explanations
    """
    try:
        substitutions = ai_substitution_service.suggest_substitutions(
            ingredient=request.ingredient,
            quantity=request.quantity,
            unit=request.unit,
            available_ingredients=request.available_ingredients
        )
        
        return SubstituteResponse(
            ingredient=request.ingredient,
            substitutions=substitutions
        )
    
    except Exception as e:
        logger.error(f"Error suggesting substitutions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ENDPOINT 3: NUTRITIONAL ANALYSIS
# ============================================================================

@router.post("/nutrition", response_model=NutritionResponse)
async def analyze_nutrition(request: NutritionRequest):
    """
    Calculate nutritional information:
    - Calories
    - Protein
    - Carbohydrates
    - Fat
    
    Adjusts dynamically when scaling changes the recipe
    """
    try:
        if not request.ingredients:
            raise HTTPException(status_code=400, detail="Ingredients list cannot be empty")
        
        # Analyze recipe nutrition
        nutrition_data = nutrition_service.analyze_recipe_nutrition(
            ingredients=request.ingredients,
            servings=request.servings
        )
        
        # Apply scaling if provided
        if request.scale_factor:
            scaled_total = {
                k: round(v * request.scale_factor, 1)
                for k, v in nutrition_data["total"].items()
            }
            scaled_per_serving = {
                k: round(v * request.scale_factor, 1)
                for k, v in nutrition_data["per_serving"].items()
            }
            
            nutrition_data["total"] = scaled_total
            nutrition_data["per_serving"] = scaled_per_serving
            nutrition_data["scale_factor"] = request.scale_factor
        
        return NutritionResponse(
            total=nutrition_data["total"],
            per_serving=nutrition_data["per_serving"],
            ingredients=nutrition_data.get("ingredients", []),
            servings=nutrition_data["servings"]
        )
    
    except Exception as e:
        logger.error(f"Error analyzing nutrition: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ENDPOINT 4: CONVERSATIONAL ASSISTANT
# ============================================================================

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatMessage):
    """
    Conversational assistant for cooking and recipe questions
    
    Features:
    - Context-aware responses using recipe information
    - Session-based conversation history
    - Dietary restriction awareness
    - Helps with scaling, substitutions, techniques, and more
    """
    try:
        if not request.message:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Set recipe context if provided
        if request.recipe_context:
            cooking_assistant.set_recipe_context(session_id, request.recipe_context)
        
        # Set dietary restrictions if provided
        if request.dietary_restrictions:
            cooking_assistant.set_dietary_restrictions(session_id, request.dietary_restrictions)
        
        # Process the message
        response = cooking_assistant.process_message(session_id, request.message)
        
        return ChatResponse(
            session_id=response["session_id"],
            user_message=response["user_message"],
            assistant_response=response["assistant_response"],
            conversation_history=response["conversation_history"]
        )
    
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/chat/session/{session_id}")
async def clear_chat_session(session_id: str):
    """Clear conversation session"""
    try:
        success = cooking_assistant.clear_session(session_id)
        return {"success": success, "message": "Session cleared" if success else "Session not found"}
    except Exception as e:
        logger.error(f"Error clearing session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """Get conversation history for a session"""
    try:
        history = cooking_assistant.get_session_history(session_id)
        return {"session_id": session_id, "conversation_history": history}
    except Exception as e:
        logger.error(f"Error retrieving history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ENDPOINT 5: MULTILINGUAL TRANSLATION
# ============================================================================

@router.post("/translate", response_model=TranslateResponse)
async def translate_content(request: TranslateRequest):
    """
    Translate recipe content to multiple languages:
    - English, Hindi, Malayalam, Tamil
    - Plus Spanish and French
    
    Can translate:
    - Single text
    - Multiple texts
    - Ingredient lists
    - Complete recipes with instructions
    """
    try:
        if not request.target_language:
            raise HTTPException(status_code=400, detail="Target language is required")
        
        # Determine what to translate and translate it
        if request.recipe:
            translated_content = translation_service.translate_recipe(
                request.recipe,
                request.target_language
            )
            return TranslateResponse(
                source_language="en",
                target_language=request.target_language,
                original=request.recipe,
                translated=translated_content
            )
        
        elif request.ingredients:
            translated_content = translation_service.translate_ingredients(
                request.ingredients,
                request.target_language
            )
            return TranslateResponse(
                source_language="en",
                target_language=request.target_language,
                original=request.ingredients,
                translated=translated_content
            )
        
        elif request.texts:
            translated_content = translation_service.translate_batch(
                request.texts,
                request.target_language
            )
            return TranslateResponse(
                source_language="en",
                target_language=request.target_language,
                original=request.texts,
                translated=translated_content
            )
        
        elif request.text:
            translated_content = translation_service.translate_text(
                request.text,
                "en",
                request.target_language
            )
            return TranslateResponse(
                source_language="en",
                target_language=request.target_language,
                original=request.text,
                translated=translated_content
            )
        
        else:
            raise HTTPException(status_code=400, detail="No content to translate provided")
    
    except Exception as e:
        logger.error(f"Error translating content: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/languages")
async def get_supported_languages():
    """Get list of supported languages for translation"""
    try:
        languages = translation_service.get_supported_languages()
        return {"supported_languages": languages}
    except Exception as e:
        logger.error(f"Error fetching languages: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get("/health")
async def health_check():
    """Health check for AI services"""
    return {
        "status": "healthy",
        "services": {
            "ingredient_extraction": "available",
            "substitution": "available",
            "nutrition": "available",
            "chat": "available",
            "translation": "available",
        }
    }
