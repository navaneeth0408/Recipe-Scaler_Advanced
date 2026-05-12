"""
AI-powered ingredient extraction service using NLP models
Identifies ingredients, predicts missing quantities, and normalizes units
"""

import logging
from typing import List, Dict, Any, Optional, Tuple, Union
import re
import os
import json
import requests
# These will be loaded lazily to speed up backend startup
pipeline = None
spacy = None
TRANSFORMERS_AVAILABLE = False
SPACY_AVAILABLE = False
# We'll check availability by attempting the import inside the lazy methods

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
    "gm": {"normalized": "gram", "grams": 1},
    "gms": {"normalized": "gram", "grams": 1},
    "gram": {"normalized": "gram", "grams": 1},
    "grams": {"normalized": "gram", "grams": 1},
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
    "flour", "maida", "wheat flour", "jaggery", "sugar", "salt", "butter", "milk", "egg", "water", "oil", "honey",
    "vanilla", "baking powder", "baking soda", "cinnamon", "nutmeg", "ginger", "garlic",
    "turmeric", "cumin", "coriander", "matcha", "cocoa", "coffee", "tea",
    "chicken", "beef", "pork", "fish", "shrimp", "mutton", "lamb", "paneer", "tofu",
    "tomato", "garlic", "onion", "carrot", "potato", "rice", "pasta", "cheese", "cream", "yogurt", "bread",
    "dal", "lentils", "chickpeas", "besan", "suji", "rava", "poha", "flattened rice",
    "grated coconut", "shredded coconut", "raw rice", "idli rice",
    "avocado", "scallions", "shallots", "cilantro", "parsley", "mayonnaise",
}

class IngredientExtractionModel:
    """Transformer-based NLP model for ingredient extraction"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._classifier = None
        self._transformers_available = TRANSFORMERS_AVAILABLE
        
        # Check if AI models should be skipped (useful for local dev with low memory)
        if os.getenv("SKIP_AI_MODELS", "false").lower() == "true":
            self.logger.info("SKIP_AI_MODELS=true: Deferred/Skipped loading heavy transformer models")
            self._transformers_available = False
        
        self.nlp = None  # spaCy model loaded on demand
        self.logger.info("Ingredient extraction model initialized")

    @property
    def classifier(self):
        """Lazy load the transformer pipeline only when needed"""
        if self._classifier is None:
            # Check environment variable to skip AI models
            if os.getenv("SKIP_AI_MODELS", "false").lower() == "true":
                self.logger.info("SKIP_AI_MODELS=true: Skipped loading BART model")
                return None
                
            try:
                global pipeline, TRANSFORMERS_AVAILABLE
                if pipeline is None:
                    self.logger.info("Lazy importing 'transformers' library...")
                    from transformers import pipeline
                    TRANSFORMERS_AVAILABLE = True
                
                self.logger.info("Loading transformer model: facebook/bart-large-mnli (this may take a moment and use significant RAM)")
                self._classifier = pipeline(
                    "zero-shot-classification",
                    model="facebook/bart-large-mnli",
                    device=-1  # CPU
                )
                self.logger.info("Transformer model loaded successfully")
            except Exception as e:
                self.logger.error(f"Failed to load transformer model: {e}. Using rule-based fallback.")
                TRANSFORMERS_AVAILABLE = False
        return self._classifier
    
    def load_spacy_model(self):
        """Lazy load spaCy model"""
        if self.nlp is None:
            try:
                global spacy, SPACY_AVAILABLE
                if spacy is None:
                    self.logger.info("Lazy importing 'spacy' library...")
                    import spacy
                    SPACY_AVAILABLE = True
                self.nlp = spacy.load("en_core_web_sm")
            except Exception:
                self.logger.warning("spaCy model or library not found. Install with: pip install spacy && python -m spacy download en_core_web_sm")
                SPACY_AVAILABLE = False
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
        # Remove leading bullets, list markers (e.g., 1., 1), *, -, •)
        # But be careful not to remove the actual quantity if it's just a number
        cleaned = re.sub(r'^[\-\*••]\s*|^\d+[\.\)]\s*', '', line)
        
        # Extract quantity and optional unit using a stricter pattern
        # Updated to capture vague terms like sprinkle, pinch, handful, to taste
        vague_terms = r"sprinkle|pinch|handful|dash|drop|salt to taste|to taste"
        units_pattern = r"kg|g|gm|gms|grams|ml|l|cups?|cup|tablespoons?|tablespoon|tbsp|tbs|teaspoons?|teaspoon|tsp|handfuls?|pinches?|pinches|dashes|drops?"
        quantity_match = re.match(
            rf"^\s*(\d+(?:\.\d+)?(?:\s+\d+/\d+)?|{vague_terms})\s*"
            rf"({units_pattern})?\s*(.*)$",
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
                quantity = quantity_match.group(1).capitalize()
            
            unit = (quantity_match.group(2) or '').strip().lower()
            ingredient_name = quantity_match.group(3).strip()
            
            # Special case: if the name is empty but quantity has 'salt', 'sugar' etc.
            # (e.g. "Salt to taste")
            if not ingredient_name:
                q_lower = quantity.lower()
                if 'salt' in q_lower:
                    ingredient_name = 'salt'
                elif 'sugar' in q_lower:
                    ingredient_name = 'sugar'
                elif 'pepper' in q_lower:
                    ingredient_name = 'pepper'
                else:
                    ingredient_name = quantity
                    quantity = ""
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
        # Don't predict if it's already a vague string quantity
        if quantity is None:
            quantity = self._predict_quantity(ingredient_name, normalized_unit)
        elif isinstance(quantity, str):
            # It's a vague quantity string, keep it as is
            pass
        
        return {
            "name": ingredient_name,
            "original_quantity": quantity,
            "quantity": quantity,
            "original_unit": unit,
            "unit": normalized_unit.get("normalized") if normalized_unit else None,
            "grams_equivalent": self._calculate_grams(quantity, normalized_unit),
            "vague_phrase": unit in ["pinch", "handful", "dash", "drop", "sprinkle"] or "taste" in str(quantity).lower() if (unit or quantity) else False,
        }
    
    def _normalize_ingredient_name(self, name: str) -> str:
        """Normalize ingredient name"""
        # Remove parenthetical notes, but keep core ingredient
        name = re.sub(r'\s*\([^)]*\)', '', name)
        # Convert to lowercase
        name = name.lower().strip()
        # Remove trailing units
        name = re.sub(r'\s+(chopped|diced|minced|sliced|shredded|melted|optional)$', '', name)
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
        Extract ingredients from text using a unified cascade:
        1. Rule-based extractor (IngredientService)
        2. LLM-based extraction if rule-based returns few results
        3. Local transformer fallback
        """
        try:
            from app.services.ingredient_service import IngredientService
            
            # 1. First pass: High-speed rule-based extraction
            ingredients = IngredientService.extract_ingredients(text)
            
            # Helper to map IngredientService format to AIIngredientService format
            def map_to_ai_format(ing_list):
                mapped = []
                for item in ing_list:
                    mapped.append({
                        "name": item.get("name", "Unknown"),
                        "quantity": item.get("quantity", 1.0),
                        "unit": item.get("unit", ""),
                        "original_quantity": item.get("quantity", 1.0),
                        "original_unit": item.get("unit", ""),
                        "vague_phrase": item.get("unit") in ["whole", "piece", "pinch", "handful", "dash", "drop", "sprinkle"] or "taste" in str(item.get("quantity", "")).lower()
                    })
                return mapped

            ai_formatted_results = map_to_ai_format(ingredients)

            # 2. Rescue Pass: If text is substantial but extraction is sparse, try LLM
            if len(ai_formatted_results) < 2 and len(text.split()) > 10:
                groq_key = os.getenv("GROQ_API_KEY")
                openai_key = os.getenv("OPENAI_API_KEY")
                if groq_key or openai_key:
                    logger.info("Rule-based pass sparse. Rescuing with LLM...")
                    llm_ingredients = self.extract_with_llm(text)
                    if llm_ingredients:
                        # Deduplicate results between rule-base and LLM (prefer LLM for complex stuff)
                        seen_names = {ing['name'].lower() for ing in ai_formatted_results}
                        for ling in llm_ingredients:
                            if ling['name'].lower() not in seen_names:
                                ai_formatted_results.append(ling)
                        return ai_formatted_results

            # 3. Fallback to local transformer only if still empty and AI models aren't skipped
            if not ai_formatted_results and os.getenv("SKIP_AI_MODELS", "false").lower() != "true":
                logger.info("Extraction still empty. Attempting local transformer fallback...")
                transformer_results = self.extractor.extract_ingredients(text)
                if transformer_results:
                    return self.extractor.handle_vague_phrases(transformer_results)

            # 4. Final Deduplication Pass
            # Resolve "cashew" vs "cashew nuts", "onions" vs "onion"
            unique_results = {}
            for ing in ai_formatted_results:
                name = ing['name'].lower().strip()
                # Use simple plural/partial matching for deduplication
                found_match = False
                for existing_name in list(unique_results.keys()):
                    if name == existing_name or name == existing_name + "s" or existing_name == name + "s":
                        found_match = True
                        # Keep the one with more detail or keep existing
                        break
                    if (len(name) > 3 and name in existing_name) or (len(existing_name) > 3 and existing_name in name):
                        found_match = True
                        if len(name) > len(existing_name):
                            unique_results[name] = ing
                            del unique_results[existing_name]
                        break
                
                if not found_match:
                    unique_results[name] = ing
            
            return list(unique_results.values())
        except Exception as e:
            logger.error(f"Error in unified ingredient extraction: {e}")
            return []

    def extract_with_llm(self, text: str) -> Optional[List[Dict[str, Any]]]:
        """
        Extract ingredients from text using a Large Language Model (Groq/OpenAI)
        Returns a structured list of ingredients.
        """
        groq_key = os.getenv("GROQ_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        
        prompt = (
            "Extract a complete and accurate list of ingredients from the following recipe text.\n"
            "Identify the name, quantity, and unit for each ingredient.\n"
            "CRITICAL: Preserve vague quantities like 'pinch', 'sprinkle', 'handful', 'to taste' as STRINGS in the 'quantity' field. "
            "Do not convert them to numerical values if they were provided as words.\n"
            "Return ONLY a valid JSON array of objects with exactly this format:\n"
            "[\n"
            "  {\n"
            "    \"name\": \"ingredient name\",\n"
            "    \"quantity\": 2.0 or \"pinch\",\n"
            "    \"unit\": \"cup\" or \"whole\" or \"\"\n"
            "  }\n"
            "]\n"
            "If an ingredient has no specific unit, use \"whole\" or an empty string.\n"
            "Text to process:\n"
            f"{text}\n"
            "Raw JSON ONLY, no markdown blocks, no explanation."
        )

        messages = [
            {"role": "system", "content": "You are a specialized recipe parsing API. Respond ONLY with valid JSON. No conversational filler."},
            {"role": "user", "content": prompt}
        ]

        try:
            response_text = ""
            if groq_key:
                resp = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    json={"model": "llama3-8b-8192", "messages": messages, "temperature": 0.1},
                    headers={"Authorization": f"Bearer {groq_key}"},
                    timeout=15
                )
                if resp.status_code == 200:
                    response_text = resp.json()["choices"][0]["message"]["content"]
            
            elif openai_key:
                resp = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    json={"model": "gpt-3.5-turbo", "messages": messages, "temperature": 0.1},
                    headers={"Authorization": f"Bearer {openai_key}"},
                    timeout=15
                )
                if resp.status_code == 200:
                    response_text = resp.json()["choices"][0]["message"]["content"]

            if response_text:
                # Basic cleaning of the response
                clean_text = response_text.strip()
                if clean_text.startswith("```"):
                    # Remove markdown blocks
                    lines = clean_text.split("\n")
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines[-1].startswith("```"):
                        lines = lines[:-1]
                    clean_text = "\n".join(lines).strip()
                
                # Find the JSON array
                start = clean_text.find('[')
                end = clean_text.rfind(']') + 1
                if start >= 0 and end > start:
                    data = json.loads(clean_text[start:end])
                    # Ensure all required fields are present
                    final_ingredients = []
                    for item in data:
                        final_ingredients.append({
                            "name": item.get("name", "Unknown"),
                            "quantity": item.get("quantity", 1.0),
                            "unit": item.get("unit", ""),
                            "original_quantity": item.get("quantity", 1.0),
                            "original_unit": item.get("unit", ""),
                            "notes": item.get("notes", ""),
                        })
                    return final_ingredients

            return None
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            return None
    
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
