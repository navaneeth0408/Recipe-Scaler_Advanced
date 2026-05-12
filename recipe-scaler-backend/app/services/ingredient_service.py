"""
Ingredient extraction and parsing service
Handles extracting structured ingredient data from raw text using a STRICT whitelist logic
and domain-specific unit mappings.
"""

import re
from typing import List, Dict, Optional, Union
from fractions import Fraction
import logging
import unicodedata

logger = logging.getLogger(__name__)

# STRICT FOOD-ONLY WHITELIST
STRICT_FOOD_WHITELIST = [
    # Core baking & staples
    "bread flour", "semolina flour", "all-purpose flour", "whole wheat flour", "flour", "maida", "wheat flour",
    "salt", "sugar", "caster sugar", "jaggery", "yeast", "water", "coconut milk", "almond milk", "oat milk", "milk",
    "butter", "unsalted butter", "clarified butter", "olive oil", "vegetable oil", "oil", "sunflower oil", "mustard oil", "coconut oil", "sesame oil", "gingelly oil", "canola oil", "peanut oil", "cooking spray",
    "egg", "eggs", "heavy cream", "sour cream", "cream cheese", "cream", "buttermilk", "whipping cream",
    "grated mozzarella cheese", "grated mozzarella", "mozzarella cheese", "mozzarella", "fontina cheese", "fontina", "parmesan", "cheddar", "ricotta", "cheese", "parmesan cheese", "grated parmesan cheese",
    "tomato sauce", "tomato paste", "tomato puree", "tomato", "tomatoes", "plum tomatoes", "diced tomatoes",
    "garlic powder", "garlic", "onion powder", "onion", "onions", "green onions", "scallions", "shallots", "purple onion", "yellow onion", "white onion",
    "red pepper flakes", "black pepper", "black peppercorns", "kali mirch", "black pepper powder", "ground black pepper", "freshly ground pepper",
    "white pepper", "white peppercorns", "chili flakes", "pepper", "red chilli flakes", "cayenne pepper", "kosher salt", "sea salt", "coarse salt",
    "basil", "oregano", "rosemary", "thyme", "paprika", "cumin", "coriander", "turmeric", "cinnamon", "curry powder", "ground cumin", "ground cinnamon", "ground ginger", "ground nutmeg", "ground coriander", "ground turmeric",
    "bay leaves", "bay leaf", "nutmeg", "cardamom", "cloves", "saffron", "saffron strands",
    "chicken stock", "beef stock", "vegetable stock", "stock", "broth", "chicken broth",
    "chicken breast", "chicken breasts", "chicken", "beef", "pork", "lamb", "mutton", "fish", "prawns", "shrimp", "salmon", "tuna", "meat", "mince", "keema", "ground beef",
    "sausage", "sausages", "bacon",
    "raw rice", "idli rice", "basmati rice", "rice", "pasta", "noodles", "bread", "pizza dough", "dough",
    "cake flour", "pastry flour", "self-rising flour",
    "lemon", "lime", "orange", "banana", "strawberry", "avocado",
    "carrot", "potato", "spinach", "mushroom", "capsicum", "green peas", "matar", "celery", "jalapeno", "cucumber",
    "broccoli", "cauliflower", "zucchini", "eggplant", "corn", "peas", "beans", "green beans", "french beans",
    "red bell pepper", "green bell pepper", "scotch bonnet bell pepper", "scotch bonnet peppers", "scotch bonnet pepper",
    "olive", "olives", "capers", "anchovies",
    "balsamic vinegar", "vinegar", "soy sauce", "worcestershire sauce", "sauce", "fish sauce", "rice vinegar", "red wine vinegar", "white vinegar",
    "maple syrup", "honey", "vanilla extract", "vanilla",
    "baking powder", "baking soda", "cornstarch", "cocoa powder", "corn flour", "corn starch",
    "dark chocolate", "white chocolate", "chocolate", "mayonnaise", "mayonaise", "salsa", "hot sauce", "dijon mustard", "mirin",
    "seasoning cube", "seasoning cubes",
    "sesame seeds", "poppy seeds", "almonds", "walnuts", "cashew nut", "cashew nuts", "kaju", "cashew", "cashews", "peanuts",
    "red wine", "white wine", "wine", "beer", "dry white wine",

    # Chillies & variations
    "red chilli", "red chillies", "red chili", "red chilies",
    "red chilly", "dry red chilli", "whole red chilli", "dry red chillies",
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
    "amchur", "dry mango powder", "turmeric powder", "haldi powder",
    "chaat masala", "pav bhaji masala", "biryani masala", "tandoori masala", "kitchen king masala",
    "melon seeds", "magaz", "khus khus", "charmagaz",
    "garam masala powder", "chaat masala powder", "asafoetida", "hing", "meat masala", "meat masala powder",

    # New Indian staples from dataset
    "white urad dal", "chana dal", "bengal gram dal", "arhar dal", "toor dal",
    "gram flour", "besan", "wheat flour", "corn flour", "jaggery",
    "coriander leaves", "dhania", "mint leaves", "pudina", "curry leaves", "kadi patta",
    "bay leaf", "tej patta", "fennel seeds", "saunf", "cumin seeds", "jeera",
    "methi seeds", "fenugreek seeds", "ajwain", "carom seeds", "peanuts", "moongphali",
    "sesame seeds", "til seeds", "badam", "almond", "mushrooms", "button mushrooms",

    # Existing Indian dairy & proteins
    "paneer", "cottage cheese", "tofu", "tempeh", "ghee", "clarified butter", "Khoa",
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
    "coconut cream", "grated coconut", "shredded coconut", "desiccated coconut", "badam", "raisins", "kishmish",
    "rose water", "kewra water", "saffron", "kesar", "yogurt", "curd", "dahi", "ginger",

    # Spelling variations
    "massala", "garam massala", "biryani massala", "chaat massala", "tandoori massala",
    # Payasam & specific Indian mixes
    "palada payasam mix", "payasam mix", "palada payasam", "vermicelli payasam",
    
    "kitchen king massala"
]
# Mapping of common variations to canonical names for deduplication
INGREDIENT_CANONICAL_MAP = {
    "turmeric powder": "turmeric",
    "coriander powder": "coriander",
    "cumin powder": "cumin",
    "black pepper powder": "black pepper",
    "ground black pepper": "black pepper",
    "red chilli powder": "red chilli",
    "chilli powder": "red chilli",
    "garlic cloves": "garlic",
    "cloves garlic": "garlic",
    "onion powder": "onion",
    "garlic powder": "garlic",
    "ginger paste": "ginger",
    "garlic paste": "garlic",
    "chilli flakes": "red chilli flakes",
    "red pepper flakes": "red chilli flakes",
    "scallions": "green onions",
    "shallots": "onion", # Shallots are small onions, often treated similarly in scaling
    "plum tomatoes": "tomato",
    "diced tomatoes": "tomato",
    "tomato puree": "tomato",
    "all-purpose flour": "flour",
    "maida": "flour", # User specific request often implies maida = flour
    "wheat flour": "flour",
    "corn starch": "cornstarch",
    "corn flour": "cornstarch",
    "meat masala powder": "meat masala",
    "flattened rice": "poha",
    "grated coconut": "desiccated coconut",
    "shredded coconut": "desiccated coconut",
    "raw rice": "rice",
    "idli rice": "rice",
    "cake flour": "flour",
    "powdered sugar": "sugar",
    "white sugar": "sugar",
}

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
        'grams': ['grams', 'gram', 'g', 'gm', 'gms', 'gms.'],
        'kilograms': ['kg', 'kilograms', 'kilogram'],
        'cups': ['cups', 'cup', 'c'],
        'tsp': ['tsp', 'teaspoon', 'teaspoons'],
        'tbsp': ['tbsp', 'tablespoon', 'tablespoons', 'table spoons', 'table spoon'],
        'ml': ['ml', 'milliliters', 'milliliter'],
        'liters': ['liters', 'liter', 'l', 'litre', 'litres'],
        'oz': ['oz', 'ounces', 'ounce'],
        'lbs': ['lbs', 'pounds', 'pound', 'lb'],
        'can': ['can', 'cans'],
        'bunch': ['bunch', 'bunches'],
        'pinch': ['pinch', 'pinches'],
        'cloves': ['clove', 'cloves'],
        'slices': ['slice', 'slices'],
        'pieces': ['piece', 'pieces'],
        'whole': ['whole', 'breasts', 'breast', 'nos', 'no', 'nos.'],
        'handful': ['handful', 'handfuls'],
        'drops': ['drop', 'drops'],
        'dash': ['dash', 'dashes'],
        'cooking spoon': ['cooking spoon', 'cooking spoons'],
        'sprinkle': ['sprinkle', 'sprinkles'],
        'inch': ['inch', 'inches'],
        'sprig': ['sprig', 'sprigs'],
        'stalk': ['stalk', 'stalks']
    }

    UNIT_MAP = {}
    for standard, variations in UNIT_VARIATIONS.items():
        for variation in variations:
            UNIT_MAP[variation.lower()] = standard
    # Extra safety for gms
    UNIT_MAP['gms'] = 'grams'
    UNIT_MAP['gm'] = 'grams'
    UNIT_MAP['gms.'] = 'grams'

    @staticmethod
    def parse_quantity(quantity_str: str) -> Union[float, str]:
        """Parses text numbers to floats or preserves vague terms as strings"""
        q = (quantity_str or "").strip().lower()
        if not q: return 1.0
        
        # Preserving vague terms as requested by USER
        if q in ['sprinkle', 'pinch', 'handful', 'a sprinkle', 'a pinch', 'a handful', 'some', 'a few', 'a little bit of', 'a little bit', 'a pinch of', 'salt to taste', 'to taste']:
            return q
            
        if q in ['a', 'an', 'one']: return 1.0
        if q == 'two': return 2.0
        if q == 'three': return 3.0
        if q == 'four': return 4.0
        if q == 'five': return 5.0
        if q == 'six': return 6.0
        if q == 'seven': return 7.0
        if q == 'eight': return 8.0
        if q == 'nine': return 9.0
        if q == 'ten': return 10.0
        if q == 'half a' or q == 'half' or q == 'a half': return 0.5
        if q == '½': return 0.5

        # Handle "or" cases, e.g., "300 or 200"
        if ' or ' in q:
            q = q.split(' or ')[0].strip()

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
        """
        Determines the semantic default unit and quantity if the user did not specify one.
        Returns a tuple of (quantity, unit) for the fallback case.
        This is called only when no quantity/unit was found in the text.
        """
        name_lower = food_name.lower()

        # ── Liquids → ml ──────────────────────────────────────────────────────
        LIQUID_ML = {
            "water", "milk", "cream", "oil", "ghee", "coconut milk", "stock",
             "rose water", "kewra water", "almond milk", "oat milk",
            "coconut cream", "cooking cream", "fresh cream", "malai",
            "olive oil", "vegetable oil", "soy sauce", "worcestershire sauce",
            "vinegar", "balsamic vinegar", "wine", "beer", "honey", "canola oil",
            "peanut oil", "maple syrup", "vanilla extract", "fish sauce", "mirin",
        }
        for item in LIQUID_ML:
            if item == name_lower:
                return "ml"

        # ── Heavy proteins & vegetables → grams ───────────────────────────────
        GRAM_ITEMS = {
            "paneer", "chicken", "beef", "lamb", "mutton", "fish", "prawns",
            "shrimp", "tofu", "meat", "mince", "keema", "salmon", "tuna",
            "potato","mushroom", "broccoli", "cauliflower", "capsicum", "spinach",
            "palak", "peas", "beans", "corn", "eggplant", "zucchini",
            "butter", "khoya", "khoa", "mawa", "cottage cheese", "cheese",
            "mozzarella",            "parmesan", "cheddar", "ricotta", "fontina",
            "chocolate", "sugar", "flour", "maida", "atta", "besan", "gram flour",
            "rice flour", "semolina", "sooji", "rava", "dal", "lentils",
            "moong dal", "chana dal", "toor dal", "urad dal", "rajma",
            "kidney beans", "chickpeas", "chana", "cashew nuts", "cashew",
            "cashew nut", "kaju", "almonds", "walnuts", "peanuts",
            "badam", "raisins", "kishmish", "desiccated coconut",
            "grated coconut", "shredded coconut",
            "tamarind", "imli", "jaggery", "wheat flour", "corn flour", "corn starch",
            "bengal gram dal", "arhar dal", "toor dal", "white urad dal",
            "meat", "mince", "keema", "ground beef", "potato", "onion",
        }
        for item in GRAM_ITEMS:
            if item == name_lower:
                return "grams"

        # ── Rice & staples → cups ─────────────────────────────────────────────
        CUP_ITEMS = {
            "rice", "basmati rice", "pasta", "noodles", "poha", "flattened rice",
            "bread flour", "all-purpose flour", "whole wheat flour",
        }
        for item in CUP_ITEMS:
            if item in name_lower:
                return "cups"

        # ── Dry spices & powders → tsp ────────────────────────────────────────
        TSP_ITEMS = {
            "salt", "pepper", "turmeric", "haldi", "cumin", "jeera",
            "coriander", "dhania", "paprika", "cinnamon", "dalchini",
            "nutmeg", "cardamom", "elaichi", "cloves", "laung",
            "garam masala", "chilli powder", "chili powder", "chilly powder",
            "red chilli powder", "red chili powder", "red chilly powder",
            "kashmiri chilli powder", "kashmiri red chilli powder",
            "kashmiri mirch", "coriander powder", "cumin powder",
            "jeera powder", "fennel powder", "saunf powder",
            "dry ginger powder", "sonth", "amchur", "dry mango powder",
            "chaat masala", "pav bhaji masala", "biryani masala",
            "tandoori masala", "kitchen king masala", "massala",
            "garam massala", "biryani massala", "chaat massala",
            "tandoori massala", "kitchen king massala", "meat masala",
            "meat masala powder",
            "baking powder", "baking soda", "cornstarch", "cocoa powder",
            "vanilla", "saffron", "kesar", "asafoetida", "hing",
            "mustard seeds", "rai", "fennel seeds", "saunf",
            "sesame seeds", "poppy seeds", "melon seeds", "magaz",
            "khus khus", "charmagaz",
        }
        for item in TSP_ITEMS:
            if item == name_lower:
                return "tsp"

        # ── Pastes → tbsp ─────────────────────────────────────────────────────
        TBSP_ITEMS = {
            "ginger garlic paste", "ginger paste", "garlic paste",
            "tomato paste", "tomato puree", "tomato sauce",
        }
        for item in TBSP_ITEMS:
            if item == name_lower:
                return "tbsp"

        # ── Dried herbs & leaves → tsp ────────────────────────────────────────
        HERB_ITEMS = {
            "basil", "oregano", "rosemary", "thyme", "kasuri methi",
            "dry fenugreek leaves", "bay leaves", "bay leaf", "tejpatta",
            "curry leaves", "kadi patta",
        }
        for item in HERB_ITEMS:
            if item == name_lower:
                return "tsp"

        # ── Dairy (curd, yogurt) → cups ───────────────────────────────────────
        CURD_ITEMS = {"curd", "dahi", "yogurt"}
        for item in CURD_ITEMS:
            if item == name_lower:
                return "cups"

        # ── Whole / countable items → whole ───────────────────────────────────
        WHOLE_ITEMS = {
            "egg", "eggs", "lemon", "lime", "orange", "apple", "banana","carrot", "onion", "onions", "tomato", "tomatoes",
            "strawberry", "garlic",  # whole bulb / clove handled above if cloves unit given
            "green chilli", "green chillies", "green chili", "red chilli",
            "red chillies", "whole red chilli", "dry red chilli",
            "star anise", "black cardamom", "badi elaichi",
            "green cardamom", "choti elaichi",
            "red bell pepper", "green bell pepper", "scotch bonnet pepper", "scotch bonnet bell pepper",
            "chicken breast", "chicken breasts"
        }
        for item in WHOLE_ITEMS:
            if item == name_lower:
                return "whole"

        # ── Default: tsp for anything spice-like, else whole ──────────────────
        spice_keywords = ["powder", "masala", "spice", "seeds", "seed", "flakes"]
        if any(kw in name_lower for kw in spice_keywords):
            return "tsp"
            
        if "yeast" in name_lower:
            return "tbsp"

        return "whole"

    @staticmethod
    def _get_default_quantity_for(food_name: str, unit: str) -> float:
        """
        Returns a sensible default QUANTITY given the food and unit.
        Called when no quantity was found in the transcript text.
        """
        name_lower = food_name.lower()

        # Quantity-by-unit heuristics
        if unit == "tsp":
            # Most spices: ½ tsp; salt/strong spices: 1 tsp
            if any(s in name_lower for s in [
                "salt", "baking powder", "baking soda", "turmeric", "haldi",
                "garam masala", "chilli powder", "chili powder", "kashmiri",
                "coriander powder", "cumin powder", "paprika",
            ]):
                return 1.0
            return 0.5

        if unit == "tbsp":
            return 1.0

        if unit == "cups":
            if any(s in name_lower for s in ["rice", "basmati", "flour", "atta"]):
                return 2.0
            if any(s in name_lower for s in ["curd", "yogurt", "dahi"]):
                return 0.5
            return 1.0

        if unit == "ml":
            if any(s in name_lower for s in ["water", "milk", "stock", "broth"]):
                return 200.0
            if any(s in name_lower for s in ["oil", "ghee"]):
                return 30.0
            if any(s in name_lower for s in ["rose water", "kewra"]):
                return 15.0
            return 50.0

        if unit == "grams":
            if any(s in name_lower for s in ["chicken", "beef", "lamb", "mutton", "fish", "meat", "mince", "keema"]):
                return 500.0
            if any(s in name_lower for s in ["paneer", "cottage cheese"]):
                return 200.0
            if any(s in name_lower for s in ["butter"]):
                return 50.0
            if any(s in name_lower for s in ["sugar", "flour", "maida", "atta", "besan"]):
                return 100.0
            if any(s in name_lower for s in ["onion", "tomato", "potato", "carrot"]):
                return 150.0
            if any(s in name_lower for s in ["cashew", "almond", "walnut", "peanut", "badam", "kaju"]):
                return 50.0
            return 100.0

        if unit == "whole":
            if any(s in name_lower for s in ["egg", "eggs"]):
                return 2.0
            if any(s in name_lower for s in ["lemon", "lime"]):
                return 1.0
            if "garlic" in name_lower:
                return 4.0   # cloves
            if any(s in name_lower for s in ["chilli", "chili", "chilly"]):
                return 2.0
            return 1.0

        return 1.0

    @staticmethod
    def extract_ingredients(text: str) -> List[Dict]:
        """
        Extract EXACTLY short 1-4 word ingredient names strictly defined within the whitelist.
        Pairs foods with preceding quantities mapping full sentences gracefully.
        Advanced deduplication resolves "cashew" vs "cashew nuts" while avoiding false exception overrides.
        """
        if not text:
            return []

        # Normalize Unicode characters (e.g. bold mathematical symbols) to plain text
        if text:
            text = unicodedata.normalize('NFKD', text)

        sentences = [s.strip() for s in re.split(r'[.!?\n]+', text) if s.strip()]

        # Accept both numeric and word quantities (common in transcripts), e.g.
        # "2 onions", "three tomatoes", "half cup milk", "a pinch of salt"
        qty_pattern = (
            r'('
            r'\d+(?:\.\d+)?(?:\s+\d+/\d+)?|\d+/\d+'          # 2, 2.5, 1 1/2, 3/4
            r'|a|an|one|two|three|four|five|six|seven|eight|nine|ten'
            r'|half|½'
            r'|sprinkle|pinch|handful'
            r')'
            r'(?:\s+or\s+\d+(?:\.\d+)?(?:\s+\d+/\d+)?|\d+/\d+)?' # Handle "300 or 200"
        )
        # Relaxed unit pattern: don't require \b at the start to handle "1cup"
        # We sort by length descending to match internal units correctly
        units = "|".join(sorted(IngredientService.UNIT_MAP.keys(), key=len, reverse=True))
        unit_pattern = rf'(?:({units})\b)?'

        results = []

        for sent in sentences:
            sent_lower = sent.lower()

            for food in STRICT_FOOD_WHITELIST:
                # Support optional 's' or 'es' for plural matching
                if re.search(rf'\b{re.escape(food)}(?:s|es)?\b', sent_lower):

                    # Allow common descriptor words between quantity and ingredient
                    # e.g. "2 medium onions", "3 large ripe tomatoes"
                    # Updated to support slashes / and parentheses () and common delimiters
                    descriptor_pattern = r'(?:(?:[\w\(\)/]+(?:-[\w\(\)/]+)?)\s+){0,3}'

                    # Relax the separators to handle various dashes and characters
                    separators = r'[-:–—\.]'

                    # Regex 1: Quantity first (Standard) - "2 cups milk"
                    regex_qty_first = rf'\b{qty_pattern}\b\s*{unit_pattern}\s*(?:of\s+)?{descriptor_pattern}{re.escape(food)}(?:s|es)?\b'
                    
                    # Regex 2: Food first (Video style) - "Beef - 1 kg" or "Onion : 2 nos"
                    # Supports separator - or : 
                    regex_food_first = rf'\b{re.escape(food)}(?:s|es)?\b\s*{separators}\s*{qty_pattern}\b\s*{unit_pattern}'

                    # Regex 3: Trailing unit (e.g. "4 sausage pieces", "3 bacon slices")
                    regex_qty_food_unit = rf'\b{qty_pattern}\b\s+{re.escape(food)}(?:s|es)?\s+({units})\b'
                    
                    matches = list(re.finditer(regex_qty_first, sent_lower))
                    is_food_first = False
                    is_trailing_unit = False
                    if not matches:
                        matches = list(re.finditer(regex_food_first, sent_lower))
                        is_food_first = True
                    if not matches:
                        matches = list(re.finditer(regex_qty_food_unit, sent_lower))
                        is_food_first = False
                        is_trailing_unit = True

                    if matches:
                        for match in matches:
                            if is_trailing_unit:
                                # In trailing_unit, qty is group 1, unit is group 2 (after food name)
                                qty_str = match.group(1)
                                unit_match = match.group(2)
                            elif is_food_first:
                                # In food_first, food is group 0 match start, qty is group 1, unit is group 2
                                qty_str = match.group(1)
                                unit_match = match.group(2)
                            else:
                                qty_str = match.group(1)
                                unit_match = match.group(2)

                            try:
                                from app.services.ingredient_service import IngredientService as _IS
                                quantity = _IS.parse_quantity(qty_str)
                            except Exception:
                                quantity = float(qty_str) if qty_str else 1.0

                            if unit_match:
                                unit = IngredientService.UNIT_MAP.get(unit_match.lower(), None)
                            else:
                                unit = None

                            # Check for trailing unit after food name (e.g. "4 sausage pieces", "3 bacon slices")
                            if unit is None and not is_food_first and not is_trailing_unit:
                                trailing_match = re.search(
                                    rf'\b{re.escape(food)}(?:s|es)?\s+({units})\b',
                                    sent_lower
                                )
                                if trailing_match:
                                    trailing_unit_str = trailing_match.group(1)
                                    unit = IngredientService.UNIT_MAP.get(trailing_unit_str.lower(), None)

                            if unit is None:
                                # For vague string quantities, we don't want to append a default unit like 'tsp'
                                if isinstance(quantity, str):
                                    unit = ""
                                else:
                                    unit = IngredientService._get_default_unit_for(food)

                            if isinstance(quantity, float) and quantity.is_integer():
                                quantity = int(quantity)

                            results.append({
                                "name": food,
                                "quantity": quantity,
                                "unit": unit
                            })
                    else:
                        # Fallback: food mentioned but no quantity found in text
                        unit = IngredientService._get_default_unit_for(food)
                        quantity = IngredientService._get_default_quantity_for(food, unit)

                        if isinstance(quantity, float) and quantity.is_integer():
                            quantity = int(quantity)

                        results.append({
                            "name": food,
                            "quantity": quantity,
                            "unit": unit
                        })

        # ────────────────────────────────────────────────
        # DEDUPLICATION PIPELINE
        # ────────────────────────────────────────────────

        # 1. Normalize Spellings and Canonical Names
        normalized_results = []
        for res in results:
            name = res['name'].lower()
            name = name.replace("chili", "chilli").replace("chilly", "chilli")
            name = name.replace("massala", "masala")
            name = name.replace("color", "colour").replace("flavor", "flavour")
            
            # Use canonical mapping if exists
            if name in INGREDIENT_CANONICAL_MAP:
                name = INGREDIENT_CANONICAL_MAP[name]
                
            res['norm_name'] = name
            normalized_results.append(res)

        # 2. Exact Match Selection
        unique_map = {}
        for res in normalized_results:
            key = res['norm_name']
            if key not in unique_map:
                unique_map[key] = res
            else:
                # Prefer entry where quantity is NOT the bare fallback default (1)
                existing_is_default = (unique_map[key]['quantity'] == 1 and
                                       unique_map[key]['unit'] in ('whole', ''))
                new_has_real_qty = not (res['quantity'] == 1 and res['unit'] in ('whole', ''))
                if new_has_real_qty and existing_is_default:
                    unique_map[key] = res

        # 3. Plural Override ("tomato" vs "tomatoes")
        names_in_map = list(unique_map.keys())
        for name in names_in_map:
            if name not in unique_map:
                continue
            plural_s = name + "s"
            plural_es = name + "es"
            if plural_s in unique_map and plural_s != name:
                del unique_map[name]
            elif plural_es in unique_map and plural_es != name:
                del unique_map[name]

        # 4. Hierarchical Substring Resolution
        DIFFERENT_INGREDIENT_MODIFIERS = {
            "powder", "paste", "puree", "sauce", "oil", "milk", "water",
            "juice", "extract", "seeds", "leaves", "stock", "broth", "flakes"
        }

        names_in_map = list(unique_map.keys())
        for name_a in names_in_map:
            if name_a not in unique_map:
                continue
            for name_b in names_in_map:
                if name_a == name_b or name_b not in unique_map or name_a not in unique_map:
                    continue
                if re.search(rf'\b{re.escape(name_a)}\b', name_b):
                    is_different = False
                    if "chilli" in name_a and "chilli powder" in name_b:
                        is_different = True
                    else:
                        extra_words = name_b.replace(name_a, "").strip().split()
                        for extra in extra_words:
                            if extra in DIFFERENT_INGREDIENT_MODIFIERS:
                                is_different = True
                                break
                    if not is_different:
                        del unique_map[name_a]

        # Remove temp field and return
        final_array = []
        for v in unique_map.values():
            if 'norm_name' in v:
                del v['norm_name']
            final_array.append(v)

        return final_array

    # ── Compatibility helpers called elsewhere in the codebase ────────────────

    @staticmethod
    def parse_ingredient(ingredient_text: str) -> Dict:
        """
        Parse a single ingredient string like "2 cups flour" into structured data.
        Used by the /ingredients/parse route.
        """
        if not ingredient_text or not ingredient_text.strip():
            return {"name": "", "quantity": 1.0, "unit": "whole", "notes": None}

        text = ingredient_text.strip()

        units = "|".join(IngredientService.UNIT_MAP.keys())
        pattern = rf'^(\d+(?:[./]\d+)?(?:\s+\d+/\d+)?)\s*({units})?\s*(.+)$'
        match = re.match(pattern, text, re.IGNORECASE)

        if match:
            qty_str = match.group(1)
            unit_str = match.group(2) or ""
            name = match.group(3).strip()
            quantity = IngredientService.parse_quantity(qty_str)
            unit = IngredientService.UNIT_MAP.get(unit_str.lower(), unit_str.lower()) if unit_str else "whole"
            return {"name": name, "quantity": quantity, "unit": unit, "notes": None}

        return {"name": text, "quantity": 1.0, "unit": "whole", "notes": None}

    @staticmethod
    def normalize_unit(unit: str) -> str:
        """Normalize a unit string to standard form."""
        if not unit:
            return "whole"
        return IngredientService.UNIT_MAP.get(unit.lower().strip(), unit.lower().strip())

    @staticmethod
    def detect_duplicates(ingredients: List[Dict]) -> List[tuple]:
        """Detect duplicate or very similar ingredients."""
        duplicates = []
        for i in range(len(ingredients)):
            for j in range(i + 1, len(ingredients)):
                name_i = (ingredients[i].get("name") or "").lower().strip()
                name_j = (ingredients[j].get("name") or "").lower().strip()
                if name_i and name_j and (name_i == name_j or name_i in name_j or name_j in name_i):
                    duplicates.append((i, j))
        return duplicates