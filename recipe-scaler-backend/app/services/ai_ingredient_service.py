"""
AI-powered ingredient extraction service using NLP models
Identifies ingredients, predicts missing quantities, and normalizes units
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
import re
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    pipeline = None
    TRANSFORMERS_AVAILABLE = False

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    spacy = None
    SPACY_AVAILABLE = False

logger = logging.getLogger(__name__)

# Unit normalization mapping
UNIT_MAPPINGS = {
    "pinch": {"normalized": "pinch", "grams": 0.5},
    "pinches": {"normalized": "pinch", "grams": 0.5},
    "handful": {"normalized": "handful", "grams": 30},
    "handfuls": {"normalized": "handful", "grams": 30},
    "dash": {"normalized": "dash", "grams": 1},
    "dashes": {"normalized": "dash", "grams": 1},
    "drop": {"normalized": "drop", "grams": 0.05},
    "drops": {"normalized": "drop", "grams": 0.05},
    "tsp": {"normalized": "teaspoon", "ml": 5},
    "teaspoon": {"normalized": "teaspoon", "ml": 5},
    "tbsp": {"normalized": "tablespoon", "ml": 15},
    "tablespoon": {"normalized": "tablespoon", "ml": 15},
    "cup": {"normalized": "cup", "ml": 240},
    "cups": {"normalized": "cup", "ml": 240},
    "ml": {"normalized": "ml", "ml": 1},
    "l": {"normalized": "liter", "ml": 1000},
    "liter": {"normalized": "liter", "ml": 1000},
    "g": {"normalized": "gram", "grams": 1},
    "gram": {"normalized": "gram", "grams": 1},
    "kg": {"normalized": "kilogram", "grams": 1000},
    "kilogram": {"normalized": "kilogram", "grams": 1000},
    "oz": {"normalized": "ounce", "grams": 28.35},
    "ounce": {"normalized": "ounce", "grams": 28.35},
    "lb": {"normalized": "pound", "grams": 453.592},
    "pound": {"normalized": "pound", "grams": 453.592},
    "piece": {"normalized": "piece", "grams": None},
    "pieces": {"normalized": "piece", "grams": None},
}

# Common ingredients for validation
COMMON_INGREDIENTS = {
    "flour", "sugar", "salt", "butter", "milk", "egg", "water", "oil", "honey",
    "vanilla", "baking powder", "baking soda", "cinnamon", "nutmeg", "ginger",
    "chicken", "beef", "pork", "fish", "shrimp", "tomato", "garlic", "onion",
    "carrot", "potato", "rice", "pasta", "cheese", "cream", "yogurt", "bread",
}

class IngredientExtractionModel:
    """Transformer-based NLP model for ingredient extraction"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        try:
            # Zero-shot classification for ingredient identification
            if TRANSFORMERS_AVAILABLE:
                self.classifier = pipeline(
                    "zero-shot-classification",
                    model="facebook/bart-large-mnli",
                    device=-1  # CPU, use device=0 for GPU
                )
            else:
                self.logger.warning("Transformers not available. Using rule-based extraction.")
                self.classifier = None
            self.nlp = None  # spaCy model loaded on demand
            self.logger.info("Ingredient extraction model initialized")
        except Exception as e:
            self.logger.warning(f"Could not load transformer model: {e}. Using rule-based extraction.")
            self.classifier = None
            self.nlp = None
    
    def load_spacy_model(self):
        """Lazy load spaCy model"""
        if self.nlp is None and SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except Exception:
                self.logger.warning("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
                self.nlp = None
    
    def extract_ingredients(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract ingredients from text using NLP
        Returns list of ingredients with extracted or predicted quantities
        """
        lines = text.split('\n')
        ingredients = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            extracted = self._parse_ingredient_line(line)
            if extracted:
                ingredients.append(extracted)
        
        return ingredients
    
    def _parse_ingredient_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse a single ingredient line"""
        # Remove leading bullets, numbers, etc.
        cleaned = re.sub(r'^[\d\.\)\-\*•]+\s*', '', line)
        
        # Extract quantity and optional unit using a stricter pattern
        quantity_match = re.match(
            r"^\s*(\d+(?:\.\d+)?(?:\s+\d+/\d+)?)\s*"
            r"(kg|g|gm|grams|ml|l|cups?|cup|tablespoons?|tablespoon|tbsp|tbs|teaspoons?|teaspoon|tsp)?\s*(.*)$",
            cleaned,
            re.IGNORECASE
        )

        if quantity_match:
            raw_qty = quantity_match.group(1)
            # try to parse fraction/decimal using IngredientService if available
            try:
                from app.services.ingredient_service import IngredientService
                quantity = IngredientService.parse_quantity(raw_qty)
            except Exception:
                # fallback to float
                quantity = float(raw_qty)

            unit = (quantity_match.group(2) or '').strip()
            ingredient_name = quantity_match.group(3).strip()
        else:
            # No explicit quantity found
            quantity = None
            unit = None
            ingredient_name = cleaned
        
        # Normalize ingredient name
        ingredient_name = self._normalize_ingredient_name(ingredient_name)
        
        if not ingredient_name:
            return None
        
        # Normalize unit if present
        normalized_unit = self._normalize_unit(unit) if unit else None
        
        # Predict missing quantity if needed
        if quantity is None:
            quantity = self._predict_quantity(ingredient_name, normalized_unit)
        
        return {
            "name": ingredient_name,
            "original_quantity": quantity,
            "quantity": quantity,
            "original_unit": unit,
            "unit": normalized_unit.get("normalized") if normalized_unit else None,
            "grams_equivalent": self._calculate_grams(quantity, normalized_unit),
            "vague_phrase": unit in ["pinch", "handful", "dash", "drop"] if unit else False,
        }
    
    def _normalize_ingredient_name(self, name: str) -> str:
        """Normalize ingredient name"""
        # Remove parenthetical notes, but keep core ingredient
        name = re.sub(r'\s*\([^)]*\)', '', name)
        # Convert to lowercase
        name = name.lower().strip()
        # Remove trailing units
        name = re.sub(r'\s+(chopped|diced|minced|sliced|shredded|grated|melted|optional)$', '', name)
        return name
    
    def _normalize_unit(self, unit: str) -> Optional[Dict[str, Any]]:
        """Normalize measurement unit"""
        if not unit:
            return None
        
        unit_lower = unit.lower().strip()
        
        # Direct match
        if unit_lower in UNIT_MAPPINGS:
            return UNIT_MAPPINGS[unit_lower]
        
        # Partial match
        for key, value in UNIT_MAPPINGS.items():
            if unit_lower.startswith(key) or key in unit_lower:
                return value
        
        return {"normalized": unit_lower, "grams": None}
    
    def _predict_quantity(self, ingredient: str, unit: Optional[Dict]) -> float:
        """Predict missing quantity based on ingredient type"""
        ingredient_lower = ingredient.lower()
        
        # Default quantities for common ingredients
        defaults = {
            "salt": 0.5,  # teaspoon
            "pepper": 0.25,  # teaspoon
            "vanilla": 1,  # teaspoon
            "baking powder": 1,  # teaspoon
            "baking soda": 0.5,  # teaspoon
            "cinnamon": 0.5,  # teaspoon
            "nutmeg": 0.25,  # teaspoon
            "ginger": 0.5,  # teaspoon
            "garlic": 2,  # cloves
            "onion": 1,  # piece
            "egg": 1,  # piece
            "butter": 2,  # tablespoons
            "oil": 2,  # tablespoons
            "water": 1,  # cup
            "milk": 1,  # cup
            "flour": 1,  # cup
        }
        
        for key, default_qty in defaults.items():
            if key in ingredient_lower:
                return default_qty
        
        return 1.0  # Default quantity
    
    def _calculate_grams(self, quantity: Optional[float], unit: Optional[Dict]) -> Optional[float]:
        """Calculate gram equivalent"""
        if quantity is None or unit is None:
            return None
        
        grams_per_unit = unit.get("grams")
        if grams_per_unit:
            return quantity * grams_per_unit
        
        return None
    
    def handle_vague_phrases(self, ingredients: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert vague phrases like 'pinch', 'handful' to standardized quantities
        """
        vague_conversions = {
            "pinch": {"quantity": 0.125, "unit": "teaspoon"},
            "handful": {"quantity": 0.5, "unit": "cup"},
            "dash": {"quantity": 0.25, "unit": "teaspoon"},
            "drop": {"quantity": 0.05, "unit": "ml"},
        }
        
        for ing in ingredients:
            if ing.get("unit") in vague_conversions:
                conversion = vague_conversions[ing["unit"]]
                ing["quantity"] = conversion["quantity"]
                ing["unit"] = conversion["unit"]
                ing["vague_phrase"] = True
        
        return ingredients

class AIIngredientService:
    """Service for AI-powered ingredient operations"""
    
    def __init__(self):
        self.extractor = IngredientExtractionModel()
    
    def extract_and_normalize_ingredients(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract ingredients from text and normalize them
        """
        try:
            ingredients = self.extractor.extract_ingredients(text)
            ingredients = self.extractor.handle_vague_phrases(ingredients)
            return ingredients
        except Exception as e:
            logger.error(f"Error extracting ingredients: {e}")
            return []
    
    def batch_extract_ingredients(self, texts: List[str]) -> List[List[Dict[str, Any]]]:
        """Extract ingredients from multiple texts"""
        results = []
        for text in texts:
            results.append(self.extract_and_normalize_ingredients(text))
        return results
    
    def validate_ingredient(self, name: str) -> bool:
        """Validate if extracted ingredient is real"""
        name_lower = name.lower()
        return any(common in name_lower for common in COMMON_INGREDIENTS)

# Global service instance
ai_ingredient_service = AIIngredientService()
