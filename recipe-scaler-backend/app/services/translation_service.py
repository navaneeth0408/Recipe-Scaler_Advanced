"""
Multilingual translation service
Supports translation for ingredients, instructions, and recipes
Languages: English, Hindi, Malayalam, Tamil
"""

import logging
from typing import Dict, List, Any, Optional
from enum import Enum
from deep_translator import GoogleTranslator

logger = logging.getLogger(__name__)

class Language(str, Enum):
    """Supported languages"""
    ENGLISH = "en"
    HINDI = "hi"
    MALAYALAM = "ml"
    TAMIL = "ta"
    SPANISH = "es"
    FRENCH = "fr"

class LanguageNames:
    """Full language names"""
    NAMES = {
        Language.ENGLISH: "English",
        Language.HINDI: "Hindi",
        Language.MALAYALAM: "Malayalam",
        Language.TAMIL: "Tamil",
        Language.SPANISH: "Spanish",
        Language.FRENCH: "French",
    }

# Translation glossary for common cooking terms
COOKING_GLOSSARY = {
    # English -> Hindi
    "en_hi": {
        "salt": "नमक",
        "sugar": "चीनी",
        "flour": "मैदा",
        "butter": "मक्खन",
        "milk": "दूध",
        "egg": "अंडा",
        "oil": "तेल",
        "water": "पानी",
        "honey": "शहद",
        "cinnamon": "दालचीनी",
        "turmeric": "हल्दी",
        "cumin": "जीरा",
        "garlic": "लहसुन",
        "onion": "प्याज",
        "tomato": "टमाटर",
        "carrot": "गाजर",
        "potato": "आलू",
        "rice": "चावल",
        "bread": "रोटी",
        "cheese": "पनीर",
        "boil": "उबालना",
        "fry": "तलना",
        "bake": "बेक करना",
        "grill": "ग्रिल करना",
        "chop": "काटना",
        "mix": "मिलाना",
        "stir": "हिलाना",
        "serve": "परोसना",
    },
    # English -> Malayalam
    "en_ml": {
        "salt": "ഉപ്പ്",
        "sugar": "പഞ്ചസാര",
        "flour": "മാവ്",
        "butter": "വെണ്ണ",
        "milk": "പാൽ",
        "egg": "മുട്ട",
        "oil": "എണ്ണ",
        "water": "വെള്ളം",
        "honey": "തേൻ",
        "garlic": "വെളുത്തുള്ളി",
        "onion": "നെങ്ങ",
        "tomato": "തക്കാളി",
        "carrot": "ഗാജര",
        "potato": "ഉരുളകിഴങ്ങ",
        "rice": "അരി",
        "bread": "പൊരോട്ട",
        "cheese": "ചീസ്",
        "boil": "തിളയ്ക്കുക",
        "fry": "വറുക",
        "bake": "ഓവനിൽ ചുട്ടെടുക്കുക",
        "grill": "ഗ്രിൽ ചെയ്യുക",
        "chop": "അരിയ്ക്കുക",
        "mix": "ഇണക്കുക",
        "stir": "കലക്കുക",
        "serve": "വിളമ്പുക",
    },
    # English -> Tamil
    "en_ta": {
        "salt": "உப்பு",
        "sugar": "சர்க்கரை",
        "flour": "மாவு",
        "butter": "வெண்ணெய்",
        "milk": "பால்",
        "egg": "முட்டை",
        "oil": "எண்ணெய்",
        "water": "தண்ணீர்",
        "honey": "தேன்",
        "garlic": "பூண்டு",
        "onion": "வெங்காயம்",
        "tomato": "தக்காளி",
        "carrot": "கேரট்",
        "potato": "உருளைக்கிழங்கு",
        "rice": "அரிசி",
        "bread": "ரொட்டி",
        "cheese": "பாலாடை",
        "boil": "கொதிக்க வைக்க",
        "fry": "பொரிக்க",
        "bake": "சுட்ட",
        "grill": "கிரில்ல் செய்ய",
        "chop": "நறுக்க",
        "mix": "கலக்க",
        "stir": "கலக்குக",
        "serve": "பரிமாற",
    },
}

class TranslationService:
    """Service for translating recipes and ingredients"""
    
    def __init__(self):
        self.glossary = COOKING_GLOSSARY
        self.logger = logging.getLogger(__name__)
    
    def translate_text(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """
        Translate text from source language to target language
        
        Args:
            text: Text to translate
            source_lang: Source language code (en, hi, ml, ta, etc.)
            target_lang: Target language code
        
        Returns:
            Translated text or None if translation fails
        """
        try:
            # Try glossary first for common terms
            glossary_key = f"{source_lang}_{target_lang}"
            translated = self._translate_with_glossary(text, glossary_key)
            if translated != text:
                return translated
            
            # Fall back to API translation
            if source_lang == target_lang:
                return text
            
            translator = GoogleTranslator(source_language=source_lang, target_language=target_lang)
            result = translator.translate(text)
            return result
        
        except Exception as e:
            self.logger.error(f"Translation error from {source_lang} to {target_lang}: {e}")
            return None
    
    def _translate_with_glossary(self, text: str, glossary_key: str) -> str:
        """
        Translate using glossary for cooking terms
        """
        if glossary_key not in self.glossary:
            return text
        
        glossary = self.glossary[glossary_key]
        result = text
        
        for english_term, translated_term in glossary.items():
            # Case-insensitive replacement
            import re
            pattern = re.compile(re.escape(english_term), re.IGNORECASE)
            result = pattern.sub(translated_term, result)
        
        return result
    
    def translate_ingredients(self, ingredients: List[Dict[str, Any]], target_lang: str) -> List[Dict[str, Any]]:
        """
        Translate ingredient list
        
        Args:
            ingredients: List of ingredient dictionaries
            target_lang: Target language code
        
        Returns:
            List of ingredients with translated names
        """
        translated = []
        
        for ing in ingredients:
            translated_ing = ing.copy()
            
            # Translate ingredient name
            original_name = ing.get("name", "")
            translated_name = self.translate_text(original_name, "en", target_lang)
            translated_ing["name"] = translated_name or original_name
            
            # Translate unit if present
            if "unit" in ing:
                translated_unit = self.translate_text(ing["unit"], "en", target_lang)
                translated_ing["unit"] = translated_unit or ing["unit"]
            
            translated.append(translated_ing)
        
        return translated
    
    def translate_recipe(self, recipe: Dict[str, Any], target_lang: str) -> Dict[str, Any]:
        """
        Translate complete recipe
        
        Args:
            recipe: Recipe dictionary with name, ingredients, instructions
            target_lang: Target language code
        
        Returns:
            Recipe with translated fields
        """
        translated = recipe.copy()
        
        # Translate name
        if "name" in recipe:
            translated["name"] = self.translate_text(recipe["name"], "en", target_lang) or recipe["name"]
        
        # Translate description
        if "description" in recipe:
            translated["description"] = self.translate_text(recipe["description"], "en", target_lang) or recipe["description"]
        
        # Translate ingredients
        if "ingredients" in recipe:
            translated["ingredients"] = self.translate_ingredients(recipe["ingredients"], target_lang)
        
        # Translate instructions
        if "instructions" in recipe:
            translated_instructions = []
            for instruction in recipe["instructions"]:
                translated_inst = self.translate_text(instruction, "en", target_lang)
                translated_instructions.append(translated_inst or instruction)
            translated["instructions"] = translated_instructions
        
        return translated
    
    def translate_batch(self, texts: List[str], target_lang: str) -> List[str]:
        """
        Translate multiple texts in batch
        
        Args:
            texts: List of texts to translate
            target_lang: Target language code
        
        Returns:
            List of translated texts
        """
        results = []
        for text in texts:
            translated = self.translate_text(text, "en", target_lang)
            results.append(translated or text)
        return results
    
    def get_supported_languages(self) -> List[Dict[str, str]]:
        """Get list of supported languages"""
        return [
            {"code": lang.value, "name": LanguageNames.NAMES.get(lang, lang.value)}
            for lang in Language
        ]
    
    def detect_language(self, text: str) -> Optional[str]:
        """
        Detect language of text
        
        Args:
            text: Text to detect language for
        
        Returns:
            Language code or None if detection fails
        """
        try:
            from langdetect import detect
            return detect(text)
        except Exception as e:
            self.logger.warning(f"Language detection failed: {e}")
            return None
    
    def add_glossary_entry(self, source_lang: str, target_lang: str, term: str, translation: str) -> bool:
        """
        Add custom glossary entry for translation
        
        Args:
            source_lang: Source language code
            target_lang: Target language code
            term: Term to add
            translation: Translation of term
        
        Returns:
            True if successful
        """
        glossary_key = f"{source_lang}_{target_lang}"
        
        if glossary_key not in self.glossary:
            self.glossary[glossary_key] = {}
        
        self.glossary[glossary_key][term.lower()] = translation
        return True
    
    def get_glossary(self, source_lang: str, target_lang: str) -> Dict[str, str]:
        """Get glossary for language pair"""
        glossary_key = f"{source_lang}_{target_lang}"
        return self.glossary.get(glossary_key, {})

# Global service instance
translation_service = TranslationService()
