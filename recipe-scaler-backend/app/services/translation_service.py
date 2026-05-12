"""
Multilingual translation service
Supports translation for ingredients, instructions, and recipes
Languages: English, Hindi, Malayalam, Tamil
"""

import logging
import re
import os
import requests
from typing import Dict, List, Any, Optional
from enum import Enum

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
        "maida": "मैदा",
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
        "coriander": "धनिया",
        "cumin": "जीरा",
        "asafoetida": "हींग",
        "jaggery": "गुड़",
        "fenugreek": "मेथी",
        "fennel": "सौंफ",
        "mint": "पुदीना",
        "curry leaves": "करी पत्ता",
        "bay leaf": "तेज पत्ता",
        "mustard": "सरसों",
        "peanuts": "मूंगफली",
        "almond": "बादाम",
        "cashew": "काजू",
        "raisins": "किशमिश",
        "saffron": "केसर",
        "scallions": "हरा प्याज",
        "avocado": "एवोकाडो",
        "mayonnaise": "मेयोनेज़",
        "shallots": "छोटे प्याज",
    },
    # English -> Malayalam
    "en_ml": {
        "salt": "ഉപ്പ്",
        "sugar": "പഞ്ചസാര",
        "flour": "മാവ്",
        "maida": "മൈദ",
        "butter": "വെണ്ണ",
        "milk": "പാൽ",
        "coconut milk": "തേങ്ങാപ്പാൽ",
        "egg": "മുട്ട",
        "oil": "എണ്ണ",
        "water": "വെള്ളം",
        "honey": "തേൻ",
        "garlic": "വെളുത്തുള്ളി",
        "ginger": "ഇഞ്ചി",
        "onion": "സവാള",
        "tomato": "തക്കാളി",
        "carrot": "ക്യാരറ്റ്",
        "potato": "ഉരുളക്കിഴങ്ങ്",
        "rice": "അരി",
        "bread": "ബ്രെഡ്",
        "cheese": "ചീസ്",
        "turmeric": "മഞ്ഞൾപ്പൊടി",
        "coriander": "മല്ലി",
        "cumin": "ജീരകം",
        "cinnamon": "കറുവാപ്പട്ട",
        "cloves": "ഗ്രാമ്പൂ",
        "cardamom": "ഏലക്ക",
        "mustard seeds": "കടുക്",
        "curry leaves": "കറിവേപ്പില",
        "green chilli": "പച്ചമുളക്",
        "red chilli": "വറ്റൽമുളക്",
        "chicken": "ചിക്കൻ",
        "beef": "ബീഫ്",
        "mutton": "മട്ടൻ",
        "pork": "പന്നിയിറച്ചി",
        "fish": "മീൻ",
        "coconut": "തേങ്ങ",
        "boil": "തിളപ്പിക്കുക",
        "fry": "വറുക്കുക",
        "bake": "ബേക്ക് ചെയ്യുക",
        "grill": "ഗ്രിൽ ചെയ്യുക",
        "chop": "അരിയുക",
        "mix": "കലർത്തുക",
        "stir": "ഇളക്കുക",
        "serve": "വിളമ്പുക",
        "coriander": "മല്ലി",
        "coriander leaves": "മല്ലിയില",
        "cumin": "ജീരകം",
        "asafoetida": "കായം",
        "jaggery": "ശർക്കര",
        "fenugreek": "ഉലുവ",
        "fennel": "പെരുംജീരകം",
        "mint": "പുതിന",
        "curry leaves": "കറിവേപ്പില",
        "bay leaf": "കറുവയില",
        "mustard": "കടുക്",
        "peanuts": "നിലക്കടല",
        "almond": "ബദാം",
        "cashew": "അണ്ടിപ്പരിപ്പ്",
        "raisins": "ഉണക്കമുന്തിരി",
        "saffron": "കുങ്കുമപ്പൂവ്",
        "hing": "കായം",
        "dhania": "മല്ലി",
        "jeera": "ജീരകം",
        "scallions": "സവാളയില",
        "avocado": "വെണ്ണപ്പഴം",
        "mayonnaise": "മയോണൈസ്",
        "shallots": "ചുവന്നുള്ളി",
        "jaggery": "ശർക്കര",
        "lemon": "നാരങ്ങ",
        "cloves": "ഗ്രാമ്പൂ",
        "cardamom": "ഏലക്ക",
        "paste": "പേസ്റ്റ്",
        "ginger garlic paste": "ഇഞ്ചി വെളുത്തുള്ളി പേസ്റ്റ്",
        "lemon juice": "നാരങ്ങാനീര്",
        "black pepper": "കുരുമുളക്",
        "vinegar": "വിനാഗിരി",
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
    
    def translate_text(self, text: str, source_lang: str, target_lang: str, context: str = "general") -> Optional[str]:
        """
        Translate text from source language to target language using APIs with fallback to glossary.
        
        Args:
            text: Text to translate
            source_lang: Source language code (en, hi, ml, ta, etc.)
            target_lang: Target language code
            context: Translation context ("general" or "ingredient")
        
        Returns:
            Translated text or None if translation fails
        """
        if not text or not text.strip():
            return text
            
        try:
            # Try glossary first for common terms
            glossary_key = f"{source_lang}_{target_lang}"
            translated = self._translate_with_glossary(text, glossary_key)
            if translated != text:
                return translated
            
            if source_lang == target_lang:
                return text
            
            # Attempt LLM API translation
            result = self._translate_with_llm(text, source_lang, target_lang, context)
            if result and result.strip() != text.strip():
                return result
                
            # Final fallback to deep_translator
            try:
                from deep_translator import GoogleTranslator
                # deep_translator uses 'ml' for malayalam, 'hi' for hindi
                translated = GoogleTranslator(source='auto', target=target_lang).translate(text)
                if translated:
                    return translated
            except Exception as e:
                self.logger.error(f"Deep translator failed: {str(e)}")
                
            # Fallback to original text if everything fails
            return text
            
        except Exception as e:
            self.logger.error(f"Translation error from {source_lang} to {target_lang}: {e}")
            return text
            
    def _translate_with_llm(self, text: str, source_lang: str, target_lang: str, context: str) -> Optional[str]:
        groq_key = os.getenv("GROQ_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        
        if not groq_key and not openai_key:
            return None
            
        system_prompt = f"You are a professional recipe translator. Translate the text from {source_lang} to {target_lang}. Return ONLY the translated text. Do not add quotes or explanations."
        
        if context == "ingredient":
            system_prompt = (
                f"You are a recipe ingredient translator. Your job is to translate ALL parts of an ingredient entry into the target language ({target_lang}) — including:\n"
                "- Ingredient names (e.g., \"tamarind\", \"coconut\", \"fenugreek leaves\", \"kasuri methi\", \"cashew nuts\", \"fish\")\n"
                "- Cooking forms and states (e.g., \"paste\", \"powder\", \"dried\", \"fresh\", \"grated\", \"chopped\")\n"
                "- Descriptors and colors (e.g., \"red\", \"green\", \"whole\", \"crushed\")\n"
                "- Spices and whole spices (e.g., \"cloves\", \"red chillies\")\n"
                "- Quantity words (e.g., \"handful\", \"a pinch\", \"a bunch\")\n"
                "- Units of measurement (e.g., \"cup\", \"tbsp\", \"tsp\", \"piece\")\n\n"
                "Do NOT leave any English word untranslated. If a word has no direct equivalent, use the closest natural phrase in the target language.\n\n"
                f"Translate EVERY word in the string from {source_lang} to {target_lang}. Return only the translated text, nothing else. No quotes, no markdown."
            )
            
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]
        
        response_text = ""
        try:
            if groq_key:
                resp = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    json={"model": "llama3-8b-8192", "messages": messages, "temperature": 0.2},
                    headers={"Authorization": f"Bearer {groq_key}"},
                    timeout=10
                )
                if resp.status_code == 200:
                    response_text = resp.json()["choices"][0]["message"]["content"]
            elif openai_key:
                resp = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    json={"model": "gpt-3.5-turbo", "messages": messages, "temperature": 0.2},
                    headers={"Authorization": f"Bearer {openai_key}"},
                    timeout=10
                )
                if resp.status_code == 200:
                    response_text = resp.json()["choices"][0]["message"]["content"]
                    
            if response_text:
                clean_text = response_text.strip().strip('"\'')
                # basic cleanup if the model hallucinates formatting
                if clean_text.lower().startswith("here is the translated text"):
                    return None 
                return clean_text
                
        except Exception as e:
            self.logger.error(f"LLM API translation failed: {e}")
            
        return None
    
    def _translate_with_glossary(self, text: str, glossary_key: str) -> str:
        """
        Translate using glossary for cooking terms
        """
        if glossary_key not in self.glossary:
            return text
        
        glossary = self.glossary[glossary_key]
        result = text
        
        # Sort keys by length (descending) to ensure longer phrases match first
        sorted_terms = sorted(glossary.keys(), key=len, reverse=True)
        
        for english_term in sorted_terms:
            translated_term = glossary[english_term]
            # Case-insensitive whole-word replacement
            pattern = re.compile(r'\b' + re.escape(english_term) + r'\b', re.IGNORECASE)
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
            if original_name:
                translated_name = self.translate_text(original_name, "en", target_lang, context="ingredient")
                translated_ing["name"] = translated_name or original_name
            
            # Translate unit if present
            if "unit" in ing and ing["unit"]:
                translated_unit = self.translate_text(ing["unit"], "en", target_lang, context="ingredient")
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
