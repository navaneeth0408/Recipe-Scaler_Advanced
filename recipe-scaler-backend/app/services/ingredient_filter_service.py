"""
Ingredient filtering utilities
Filters transcripts to extract ingredient-related sentences using a STRICT food whitelist.
"""

import re
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
    "paneer", "cottage cheese", "tofu", "tempeh", "ghee", "clarified butter",
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

# Sort whitelist by length descending to match longest ingredients first (e.g. "bread flour" before "flour")
STRICT_FOOD_WHITELIST.sort(key=len, reverse=True)


def filter_ingredient_sentences(transcript: str) -> str:
    """
    Filter transcript to extract only ingredient-related sentences
    using the strict food whitelist.
    
    Args:
        transcript: Full transcribed text from video
        
    Returns:
        Filtered text containing only sentences with whitelist food keywords
    """
    if not transcript or not isinstance(transcript, str):
        logger.warning("Invalid transcript provided")
        return ""

    try:
        # Split into sentences using punctuation and newlines
        sentences = [s.strip() for s in re.split(r'[.!?\n]+', transcript) if s.strip()]
        
        filtered_sentences = []
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            # Check if sentence contains ANY food keyword from the STRICT whitelist
            has_food = False
            for kw in STRICT_FOOD_WHITELIST:
                # Use word boundaries to prevent matching "egg" in "leg"
                if re.search(rf'\b{re.escape(kw)}\b', sentence_lower):
                    has_food = True
                    break
            
            # Keep ONLY sentences that clearly mention a food ingredient.
            # REMOVE sentences that are pure cooking instructions with no food noun:
            if has_food:
                filtered_sentences.append(sentence)
                logger.debug(f"Included ingredient sentence: {sentence[:80]}...")
            else:
                logger.debug(f"Excluded non-food sentence: {sentence[:80]}...")
        
        if not filtered_sentences:
            return ""
            
        return ". ".join(filtered_sentences) + "."
        
    except Exception as e:
        logger.error(f"Error filtering ingredient sentences: {str(e)}")
        # In case of error, return empty string as per rules
        return ""


def extract_ingredient_phrases(transcript: str, max_phrases: int = 50) -> list:
    """Legacy helper mapping for fallback"""
    return []
