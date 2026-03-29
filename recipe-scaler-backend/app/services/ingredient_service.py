"""
Ingredient extraction and parsing service
Handles extracting structured ingredient data from raw text using a STRICT whitelist logic
and domain-specific unit mappings.
"""

import re
from typing import List, Dict, Optional
from fractions import Fraction
import logging

logger = logging.getLogger(__name__)

# STRICT FOOD-ONLY WHITELIST
STRICT_FOOD_WHITELIST = [
    # Core baking & staples
    "bread flour", "semolina flour", "all-purpose flour", "whole wheat flour", "flour",
    "salt", "sugar", "yeast", "water", "coconut milk", "almond milk", "oat milk", "milk",
    "butter", "olive oil", "vegetable oil", "oil",
    "egg", "eggs", "heavy cream", "sour cream", "cream cheese", "cream",
    "mozzarella cheese", "mozzarella", "fontina cheese", "fontina", "parmesan", "cheddar", "ricotta", "cheese",
    "tomato sauce", "tomato paste", "tomato puree", "tomato", "tomatoes",
    "garlic powder", "garlic", "onion powder", "onion", "onions",
    "red pepper flakes", "black pepper", "black peppercorns", "kali mirch", 
    "white pepper", "white peppercorns", "chili flakes", "pepper",
    "basil", "oregano", "rosemary", "thyme", "paprika", "cumin", "coriander", "turmeric", "cinnamon",
    "bay leaves", "bay leaf", "nutmeg", "cardamom", "cloves",
    "chicken stock", "beef stock", "vegetable stock", "stock", "broth",
    "chicken", "beef", "pork", "lamb", "mutton", "fish", "prawns", "shrimp", "salmon", "tuna", "meat", "mince", "keema",
    "rice", "pasta", "noodles", "bread", "pizza dough", "dough",
    "lemon", "lime", "orange", "apple", "banana", "strawberry",
    "carrot", "potato", "spinach", "mushroom", "capsicum",
    "broccoli", "cauliflower", "zucchini", "eggplant", "corn", "peas", "beans",
    "olive", "olives", "capers", "anchovies",
    "balsamic vinegar", "vinegar", "soy sauce", "worcestershire sauce", "sauce",
    "maple syrup", "honey", "vanilla extract", "vanilla",
    "baking powder", "baking soda", "cornstarch", "cocoa powder",
    "dark chocolate", "white chocolate", "chocolate",
    "sesame seeds", "poppy seeds", "almonds", "walnuts", "cashew nut", "cashew nuts", "kaju", "cashew", "cashews", "peanuts",
    "red wine", "white wine", "wine", "beer",
    
    # Chillies & variations
    "red chilli", "red chillies", "red chili", "red chilies",
    "red chilly", "dry red chilli", "whole red chilli",
    "green chilli", "green chillies", "green chili", "green chilies", "green chilly",
    "chilli powder", "chilly powder", "chili powder",
    "red chilli powder", "red chilly powder", "red chili powder",
    "kashmiri chilli", "kashmiri chili", "kashmiri chilly",
    "kashmiri mirch", "kashmiri chilli powder",
    "kashmiri red chilli powder",
    
    # Khoya variations
    "khoa", "khoya", "mawa", "khoa mawa", "dried milk solids", "evaporated milk solids",
    
    # Other new Indian bases & spices
    "malai", "fresh cream", "cooking cream",
    "ginger garlic paste", "ginger paste", "garlic paste",
    "whole spices", "whole garam masala",
    "black cardamom", "badi elaichi",
    "green cardamom", "choti elaichi",
    "coriander powder", "cumin powder", "jeera powder",
    "fennel powder", "saunf powder",
    "dry ginger powder", "sonth",
    "amchur", "dry mango powder",
    "chaat masala", "pav bhaji masala", "biryani masala", "tandoori masala", "kitchen king masala",
    "melon seeds", "magaz", "khus khus", "charmagaz",
    
    # Existing Indian dairy & proteins
    "paneer", "cottage cheese", "tofu", "tempeh", "ghee", "clarified butter","Khoa"
    # Existing Indian spices & aromatics
    "garam masala", "haldi", "jeera", "dhania", "elaichi", "laung", "dalchini",
    "tejpatta", "star anise", "fennel seeds", "saunf", "mustard seeds", "rai", 
    "fenugreek", "methi", "asafoetida", "hing", "kasuri methi", 
    "dry fenugreek leaves", "curry leaves", "kadi patta",
    # Existing Indian vegetables & produce
    "bitter gourd", "karela", "drumstick", "moringa", "raw banana", "bottle gourd",
    "lauki", "ridge gourd", "tinda", "ivy gourd", "fenugreek leaves", "palak", "amaranth",
    # Existing Indian staples
    "basmati rice", "dal", "lentils", "moong dal", "chana dal", "toor dal", "urad dal",
    "rajma", "kidney beans", "chickpeas", "chana", "besan", "gram flour", "rice flour",
    "atta", "semolina", "sooji", "rava", "poha", "flattened rice", "tamarind", "imli", "kokum",
    # Existing Indian sauces & condiments
    "coconut cream", "desiccated coconut", "badam", "raisins", "kishmish",
    "rose water", "kewra water", "saffron", "kesar", "yogurt", "curd", "dahi", "ginger",
    
    # Spelling variations
    "massala", "garam massala", "biryani massala", "chaat massala", "tandoori massala",
    "kitchen king massala", "color", "colour", "food color", "food colour",
    "flavor", "flavour", "flavoring", "flavouring"
]

# Sort whitelist by length descending to match longest ingredients first
STRICT_FOOD_WHITELIST.sort(key=len, reverse=True)


class IngredientService:
    """Service for parsing and extracting short 1-4 word whitelist ingredients from text"""
    
    _nlp = None

    @classmethod
    def get_nlp(cls):
        return None

    # Quantities Mapping to User Preferences
    UNIT_VARIATIONS = {
        'grams': ['grams', 'gram', 'g', 'gm'],
        'kilograms': ['kg', 'kilograms', 'kilogram'],
        'cups': ['cups', 'cup', 'c'],
        'tsp': ['tsp', 'teaspoon', 'teaspoons'],
        'tbsp': ['tbsp', 'tablespoon', 'tablespoons'],
        'ml': ['ml', 'milliliters', 'milliliter'],
        'liters': ['liters', 'liter', 'l'],
        'oz': ['oz', 'ounces', 'ounce'],
        'lbs': ['lbs', 'pounds', 'pound', 'lb'],
        'can': ['can', 'cans'],
        'bunch': ['bunch', 'bunches'],
        'pinch': ['pinch', 'pinches'],
        'cloves': ['clove', 'cloves'],
        'slices': ['slice', 'slices'],
        'whole': ['whole', 'piece', 'pieces'],
        'handful': ['handful', 'handfuls'],
        'drops': ['drop', 'drops'],
        'dash': ['dash', 'dashes']
    }
    
    UNIT_MAP = {}
    for standard, variations in UNIT_VARIATIONS.items():
        for variation in variations:
            UNIT_MAP[variation.lower()] = standard

    @staticmethod
    def parse_quantity(quantity_str: str) -> float:
        """Parses text numbers to floats"""
        q = (quantity_str or "").strip().lower()
        if not q or q in ['a', 'an', 'one', 'some', 'a few', 'a little bit of', 'a little bit', 'a pinch of']: return 1.0
        if q == 'two': return 2.0
        if q == 'three': return 3.0
        if q == 'four': return 4.0
        if q == 'half a' or q == 'half' or q == 'a half': return 0.5
        
        try:
            if '/' in q:
                parts = q.split()
                total = 0.0
                for part in parts:
                    if '/' in part:
                        total += float(Fraction(part))
                    else:
                        total += float(part)
                return total if total > 0 else 1.0
            return float(q)
        except Exception:
            return 1.0

    @staticmethod
    def _get_default_unit_for(food_name: str) -> str:
        """Determines the semantic default unit if the user did not specify one."""
        name_lower = food_name.lower()
        
        # Categorized sets for default bindings based on user rules
        GRAMS_DEFAULTS = {
            "paneer", "chicken", "beef", "lamb", "mutton", "fish", "prawns", 
            "shrimp", "tofu", "meat", "mince", "keema"
        }
        ML_DEFAULTS = {
            "water", "milk", "cream", "oil", "ghee", "coconut milk", "stock", 
            "broth", "rose water", "kewra water"
        }
        
        # Exact match or broad coverage (e.g. "cooking cream" -> matches "cream" substring loop or direct logic)
        for g_item in GRAMS_DEFAULTS:
            if g_item in name_lower:
                return "grams"
                
        for m_item in ML_DEFAULTS:
            if m_item in name_lower:
                return "ml"
                
        return "" # For all other ingredients, default to empty string

    @staticmethod
    def extract_ingredients(text: str) -> List[Dict]:
        """
        Extract EXACTLY short 1-4 word ingredient names strictly defined within the whitelist.
        Pairs foods with preceding quantities mapping full sentences gracefully.
        Advanced deduplication resolves "cashew" vs "cashew nuts" while avoiding false exception overrides.
        """
        if not text:
            return []
            
        sentences = [s.strip() for s in re.split(r'[.!?\n]+', text) if s.strip()]
        
        qty_pattern = r'(\d+(?:\.\d+)?|\d+/\d+|\d+\s+\d+/\d+|half a|half|a half|a few|a little bit of|some|a|an|one|two|three|four|five|six|seven|eight|nine|ten)'
        # Need to dynamically append standard terms to support variations mapping in Regex
        units = "|".join(IngredientService.UNIT_MAP.keys())
        unit_pattern = rf'(?:({units}))?'
        
        results = []
        
        for sent in sentences:
            sent_lower = sent.lower()
            
            # Simple approach: Search for any whitelist item in sentence.
            # If present, attempt to find its full measurement phrase.
            for food in STRICT_FOOD_WHITELIST:
                if re.search(rf'\b{re.escape(food)}\b', sent_lower):
                    
                    # Pattern cleanly anchors digits, spacing, unit, and "of" right up to the food name
                    regex = rf'\b{qty_pattern}\s*{unit_pattern}\s*(?:of\s+)?(?:(?:the|some|fresh|organic)\s+)?{re.escape(food)}\b'
                    matches = list(re.finditer(regex, sent_lower))
                    
                    if matches:
                        for match in matches:
                            qty_str = match.group(1)
                            qty = IngredientService.parse_quantity(qty_str)
                            
                            unit_match = match.group(2)
                            if unit_match:
                                unit = IngredientService.UNIT_MAP.get(unit_match.lower(), None)
                            else:
                                unit = None
                                
                            if unit is None:
                                unit = IngredientService._get_default_unit_for(food)
                                
                            if isinstance(qty, float) and qty.is_integer():
                                qty = int(qty)
                                
                            results.append({
                                "name": food,
                                "quantity": qty,
                                "unit": unit
                            })
                    else:
                        # Fallback: We know it's in the sentence but it has no cleanly attached quantity 
                        # meaning it was mentioned generically ("add the cashews to the top")
                        qty = 1.0
                        unit = IngredientService._get_default_unit_for(food)
                        
                        if isinstance(qty, float) and qty.is_integer():
                            qty = int(qty)
                            
                        results.append({
                            "name": food,
                            "quantity": qty,
                            "unit": unit
                        })
                        
        # ----------------------------------------------------
        # DEDUPLICATION PIPELINE
        # ----------------------------------------------------

        # 1. Normalize Spellings
        normalized_results = []
        for res in results:
            name = res['name'].lower()
            name = name.replace("chili", "chilli").replace("chilly", "chilli")
            name = name.replace("massala", "masala")
            name = name.replace("color", "colour").replace("flavor", "flavour")
            res['norm_name'] = name
            normalized_results.append(res)

        # 2. Exact Match Selection
        unique_map = {}
        for res in normalized_results:
            key = res['norm_name']
            if key not in unique_map:
                unique_map[key] = res
            else:
                # Prioritize valid quantity mappings over default 1.0s
                if res['quantity'] != 1 and unique_map[key]['quantity'] == 1:
                    unique_map[key] = res

        # 3. Plural Override ("tomato" vs "tomatoes")
        names_in_map = list(unique_map.keys())
        for name in names_in_map:
            if name not in unique_map: continue
            
            plural_s = name + "s"
            plural_es = name + "es"
            
            if plural_s in unique_map and plural_s != name:
                logger.debug(f"Retaining {plural_s} over {name}")
                del unique_map[name]
            elif plural_es in unique_map and plural_es != name:
                logger.debug(f"Retaining {plural_es} over {name}")
                del unique_map[name]

        # 4. Hierarchical Substring Resolution (Keep "cashew nuts", drop "cashew")
        # Except if modifiers explicitly denote drastically different products
        DIFFERENT_INGREDIENT_MODIFIERS = {
            "powder", "paste", "puree", "sauce", "oil", "milk", "water", 
            "juice", "extract", "seeds", "leaves", "stock", "broth", "flakes"
        }
        
        names_in_map = list(unique_map.keys())
        for name_a in names_in_map:
            if name_a not in unique_map: continue
            
            for name_b in names_in_map:
                if name_a == name_b or name_b not in unique_map or name_a not in unique_map:
                    continue
                    
                # A is a subset of B
                if re.search(rf'\b{re.escape(name_a)}\b', name_b):
                    
                    is_different = False
                    
                    if "chilli" in name_a and "chilli powder" in name_b:
                        is_different = True
                    else:
                        # E.g. "fresh cream" - "cream" -> "fresh " remaining modifier check
                        extra_words = name_b.replace(name_a, "").strip().split()
                        for extra in extra_words:
                            if extra in DIFFERENT_INGREDIENT_MODIFIERS:
                                is_different = True
                                break
                    
                    if not is_different:
                        # They describe identical bases (e.g. "cashew" vs "cashew nuts")
                        # We delete the inferior shortened version A
                        logger.debug(f"Removing '{name_a}' in favor of longer '{name_b}'")
                        del unique_map[name_a]

        # Remove our temporary normalized field helper before API delivery
        final_array = []
        for v in unique_map.values():
            if 'norm_name' in v:
                del v['norm_name']
            final_array.append(v)
            
        return final_array
