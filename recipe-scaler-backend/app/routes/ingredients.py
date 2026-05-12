"""
Route handlers for ingredient operations
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import uuid
import logging
from typing import List, Optional

from app.models.schemas import (
    IngredientRequest,
    ExtractedIngredientsResponse,
    Ingredient,
)
from app.services.ingredient_service import IngredientService
from app.services.translation_service import translation_service, Language
from app.database.db import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ingredients", tags=["ingredients"])


# ============================================================================
# CUSTOM REQUEST/RESPONSE MODELS
# ============================================================================

class ParseIngredientsRequest(BaseModel):
    """Request model for parsing ingredients from YouTube description"""
    text: str = Field(..., description="YouTube video description or ingredient text")
    serving_size: Optional[int] = Field(default=None, description="Original serving size")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Ingredients:\n2 cups flour\n1/2 cup sugar\n3 eggs",
                "serving_size": 4
            }
        }


class ParseIngredientsResponse(BaseModel):
    """Response model for parsed ingredients"""
    ingredients: List[Ingredient]
    extracted_count: int
    serving_size: Optional[int] = None
    original_language: Optional[str] = None
    translated_language: Optional[str] = None
    success: bool

    class Config:
        json_schema_extra = {
            "example": {
                "ingredients": [
                    {"name": "flour", "quantity": 2, "unit": "cup"},
                    {"name": "sugar", "quantity": 0.5, "unit": "cup"},
                    {"name": "eggs", "quantity": 3, "unit": "whole"}
                ],
                "extracted_count": 3,
                "serving_size": 4,
                "success": True
            }
        }


@router.post("/extract", response_model=ExtractedIngredientsResponse)
def extract_ingredients(
    request: IngredientRequest,
    db: Session = Depends(get_db)
):
    """
    Extract structured ingredients from raw text
    
    Takes a text string of ingredients (comma-separated or newline-separated)
    and returns a structured list of ingredients with quantities, units, and names.
    
    Example request:
    ```json
    {
        "text": "2 cups flour, 1/2 cup sugar, 3 eggs, 1 tsp vanilla",
        "serving_size": 4
    }
    ```
    """
    try:
        if not request.text or request.text.strip() == '':
            return ExtractedIngredientsResponse(
                ingredients=[],
                serving_size=request.serving_size,
                extracted_count=0,
                success=False
            )

        # Extract ingredients from text
        parsed_ingredients = IngredientService.extract_ingredients(request.text)

        # Detect duplicates
        duplicates = IngredientService.detect_duplicates(parsed_ingredients)
        if duplicates:
            logger.info(f"Found {len(duplicates)} potential duplicate ingredients")

        # Convert to Ingredient models
        ingredients = []
        for ing in parsed_ingredients:
            ingredients.append(
                Ingredient(
                    name=ing['name'],
                    quantity=ing['quantity'],
                    unit=ing['unit'],
                    notes=ing.get('notes'),
                )
            )

        return ExtractedIngredientsResponse(
            ingredients=ingredients,
            serving_size=request.serving_size,
            extracted_count=len(ingredients),
            success=True
        )

    except Exception as e:
        logger.error(f"Error extracting ingredients: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/parse", response_model=ParseIngredientsResponse)
def parse_ingredients_from_text(
    request: ParseIngredientsRequest,
    db: Session = Depends(get_db)
):
    """
    Parse ingredients from raw text (e.g., YouTube description)
    
    This endpoint mimics the frontend parseIngredients() function.
    It intelligently extracts ingredients from text that may contain
    mixed instructions, formatting, etc.
    
    Uses advanced filtering to:
    - Identify ingredient sections (looking for "Ingredients:" markers)
    - Skip instruction lines
    - Extract quantities, units, and names
    - Filter out unnecessary keywords
    
    Example request:
    ```json
    {
        "text": "Ingredients:\\n2 cups flour\\n1/2 cup sugar\\n3 eggs\\n\\nInstructions:\\n1. Mix flour...",
        "serving_size": 4
    }
    ```
    """
    try:
        if not request.text or request.text.strip() == '':
            return ParseIngredientsResponse(
                ingredients=[],
                extracted_count=0,
                serving_size=request.serving_size,
                original_language=None,
                translated_language=None,
                success=False
            )

        # ------------------------------------------------------------------
        # Language detection & optional Malayalam → English translation
        # ------------------------------------------------------------------
        original_text = request.text
        text_for_parsing = original_text

        detected_lang = translation_service.detect_language(original_text)
        translated_lang: Optional[str] = None

        if detected_lang == Language.MALAYALAM.value:
            # Translate full text from Malayalam to English before parsing.
            translated = translation_service.translate_text(
                original_text,
                source_lang=Language.MALAYALAM.value,
                target_lang=Language.ENGLISH.value,
            )
            if translated:
                text_for_parsing = translated
                translated_lang = Language.ENGLISH.value
        else:
            # For English or any other language, keep the original text.
            text_for_parsing = original_text

        # Define units and keywords (matching frontend logic)
        units = [
            'cup', 'cups', 'teaspoon', 'teaspoons', 'tablespoon', 'tablespoons', 
            'tbsp', 'tsp', 'gram', 'grams', 'g', 'kg', 'kilogram', 'kilograms', 
            'ounce', 'ounces', 'oz', 'lb', 'pound', 'pounds', 'ml', 'milliliter', 
            'milliliters', 'liter', 'liters', 'l', 'dash', 'pinch', 'handful',
            'clove', 'cloves', 'bunch', 'can', 'cans', 'jar', 'jars', 'slice', 'slices'
        ]
        
        unnecessary_keywords = [
            'degree', 'minutes', 'oven', 'preheat', 'temperature', 'time', 
            'instagram', 'http', 'https', 'video', 'subscribe', 'cook', 'cooking',
            'yield', 'serves', 'servings', 'written', 'follow', 'comment', 'like'
        ]
        
        instruction_indicators = [
            'stir', 'mix', 'combine', 'heat', 'add', 'put', 'place', 'rub', 'coat',
            'sprinkle', 'bake', 'boil', 'simmer', 'chop', 'dice', 'slice', 'prepare',
            'wash', 'clean', 'drain', 'strain', 'grill', 'broil', 'season', 'marinate',
            'rest', 'cool', 'chill', 'refrigerate', 'store', 'pour', 'transfer',
            'remove', 'discard', 'serve', 'garnish', 'top', 'arrange', 'assemble',
            'until', 'when', 'while', 'then', 'next', 'step', 'repeat', 'continue'
        ]

        # Split text into lines
        lines = text_for_parsing.split('\n')
        
        # Find ingredient section markers
        start_line = -1
        end_line = len(lines)
        
        for i, line in enumerate(lines):
            lower_line = line.lower()
            if 'ingredient' in lower_line and ':' in lower_line:
                start_line = i + 1
            if start_line >= 0 and ('instruction' in lower_line or 'direction' in lower_line):
                end_line = i
                break
        
        # Use ingredient section if found, otherwise analyze whole text
        ingredient_range = lines[start_line:end_line] if start_line >= 0 else lines
        
        # Filter and extract ingredients
        extracted_ingredients = []
        
        for line in ingredient_range:
            lower_line = line.lower().strip()
            
            # Skip empty lines and short lines
            if len(lower_line) < 3:
                continue
            
            # Skip separator lines (dashes, stars, etc)
            if all(c in '-*=' for c in lower_line if c != ' '):
                continue
            
            # Skip lines with unnecessary keywords
            if any(keyword in lower_line for keyword in unnecessary_keywords):
                continue
            
            # Skip lines that are step numbers (1., 2., etc)
            if lower_line[0].isdigit() and lower_line[1] == '.':
                continue
            
            # Skip lines that start with instruction keywords
            line_without_prefix = lower_line.lstrip('0123456789 .').strip()
            if any(line_without_prefix.startswith(ind) for ind in instruction_indicators):
                continue
            
            # Skip very long lines without commas (likely instructions)
            if len(lower_line.split()) > 10 and ',' not in lower_line:
                continue
            
            # Check if line contains ingredient indicators
            has_unit = any(f' {unit} ' in f' {lower_line} ' or f' {unit}s ' in f' {lower_line} ' 
                          for unit in units)
            starts_with_number = lower_line[0].isdigit() or lower_line[0] == '('
            has_bullet = lower_line[0] in '-•*'
            
            if has_unit or starts_with_number or has_bullet:
                # Clean up the line (remove emojis and control characters)
                import re
                clean_line = re.sub(r'[\U0001F000-\U0001FFFF]', '', line)  # Remove emojis
                clean_line = clean_line.lstrip('-•* ').strip()
                
                if clean_line and not all(c in '-*=' for c in clean_line.replace(' ', '')):
                    extracted_ingredients.append(clean_line)
        
        # Parse each ingredient string strictly using the whitelist service
        ingredients = []
        for ingredient_text in extracted_ingredients:
            try:
                # Use extract_ingredients instead of parse_ingredient, 
                # to strictly enforce STIRCT_FOOD_WHITELIST and prevent garbage items like "the"
                strict_matches = IngredientService.extract_ingredients(ingredient_text)
                
                for parsed in strict_matches:
                    if parsed and parsed.get('name', '').strip():
                        ingredients.append(
                            Ingredient(
                                name=parsed['name'],
                                quantity=parsed['quantity'],
                                unit=parsed['unit'],
                                notes=parsed.get('notes')
                            )
                        )
            except Exception as e:
                logger.warning(f"Could not parse ingredient strictly '{ingredient_text}': {str(e)}")
                # Do NOT fallback to parsing everything loosely to prevent "a", "the", "for" from getting added.

        return ParseIngredientsResponse(
            ingredients=ingredients,
            extracted_count=len(ingredients),
            serving_size=request.serving_size,
            original_language=detected_lang,
            translated_language=translated_lang,
            success=len(ingredients) > 0
        )

    except Exception as e:
        logger.error(f"Error parsing ingredients: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/normalize")
def normalize_units(
    ingredients: list[Ingredient],
    db: Session = Depends(get_db)
):
    """
    Normalize ingredient units to standard forms
    
    Converts various unit variations to standard forms (cup, tbsp, tsp, etc)
    """
    try:
        normalized = []
        for ing in ingredients:
            normalized_unit = IngredientService.normalize_unit(ing.unit)
            normalized.append({
                'name': ing.name,
                'quantity': ing.quantity,
                'unit': normalized_unit,
                'notes': ing.notes,
            })

        return {
            'ingredients': normalized,
            'success': True,
        }

    except Exception as e:
        logger.error(f"Error normalizing units: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/detect-duplicates")
def detect_duplicate_ingredients(
    ingredients: list[Ingredient],
    db: Session = Depends(get_db)
):
    """
    Detect duplicate or very similar ingredients
    
    Returns list of ingredient pairs that appear to be duplicates
    """
    try:
        # Convert to dict format
        ing_dicts = [ing.model_dump() for ing in ingredients]

        # Detect duplicates
        duplicates = IngredientService.detect_duplicates(ing_dicts)

        result = {
            'duplicates': [
                {
                    'index1': dup[0],
                    'index2': dup[1],
                    'ingredient1': ingredients[dup[0]].model_dump(),
                    'ingredient2': ingredients[dup[1]].model_dump(),
                }
                for dup in duplicates
            ],
            'count': len(duplicates),
            'success': True,
        }

        return result

    except Exception as e:
        logger.error(f"Error detecting duplicates: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
