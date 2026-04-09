"""
AI-powered ingredient substitution service
Suggests alternatives based on availability, categories, and practical cooking replacements.
"""

import logging
from typing import List, Dict, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)

# Substitution database (Fallback rules focused purely on practicality, not diet)
SUBSTITUTIONS = {
    "butter": [
        {
            "name": "oil",
            "ratio": "3/4",
            "ratio_float": 0.75,
            "note": "Closest fat replacement for baking and cooking",
        },
        {
            "name": "margarine",
            "ratio": "1:1",
            "ratio_float": 1.0,
            "note": "Direct 1:1 substitute in almost all recipes",
        },
    ],
    "milk": [
        {
            "name": "water + milk powder",
            "ratio": "1:1",
            "ratio_float": 1.0,
            "note": "Mix water with milk powder for exact replication",
        },
        {
            "name": "cream + water",
            "ratio": "0.5 + 0.5",
            "ratio_float": 1.0,
            "note": "Diluted cream mimics whole milk richness",
        },
    ],
    "garlic": [
        {
            "name": "garlic powder",
            "ratio": "1/8",
            "ratio_float": 0.125,
            "note": "1/8 tsp powder per clove",
        }
    ],
    "fresh herbs": [
        {
            "name": "dried herbs",
            "ratio": "1/3",
            "ratio_float": 0.33,
            "note": "1 tsp dried per 1 tbsp fresh",
        }
    ],
    "egg": [
        {
            "name": "applesauce",
            "ratio": "1/4 cup",
            "ratio_float": 0.25,
            "note": "Works for moist baked goods",
        },
        {
            "name": "yogurt",
            "ratio": "1/4 cup",
            "ratio_float": 0.25,
            "note": "Good for baking and binding",
        }
    ],
    "sugar": [
        {
            "name": "honey",
            "ratio": "3/4",
            "ratio_float": 0.75,
            "note": "Use less as it is sweeter and adds liquid",
        },
        {
            "name": "brown sugar",
            "ratio": "1:1",
            "ratio_float": 1.0,
            "note": "Direct substitute, adds slight molasses flavor",
        }
    ],
    "ginger": [
        {
            "name": "ground ginger powder",
            "ratio": "1/4",
            "ratio_float": 0.25,
            "note": "Use 1/4 tsp ground dried ginger per 1 tbsp fresh",
        }
    ],
    "chilli": [
        {
            "name": "red chilli powder / cayenne pepper",
            "ratio": "1/2",
            "ratio_float": 0.5,
            "note": "Dry powder is more concentrated than fresh chillies",
        },
        {
            "name": "jalapenos or bell peppers",
            "ratio": "1:1",
            "ratio_float": 1.0,
            "note": "For fresh crunch without as much heat",
        }
    ],
    "turmeric": [
        {
            "name": "curry powder",
            "ratio": "1:1",
            "ratio_float": 1.0,
            "note": "Contains turmeric but adds other flavors",
        },
        {
            "name": "saffron",
            "ratio": "pinch",
            "ratio_float": 0.1,
            "note": "For color substitute (very expensive though)",
        }
    ]
}

class AISubstitutionService:
    """Service for AI-powered ingredient substitution"""
    
    def __init__(self):
        self.substitutions = SUBSTITUTIONS
    
    def suggest_substitutions(
        self,
        ingredient: str,
        quantity: float,
        unit: str,
        available_ingredients: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Suggest ingredient substitutions based on AI model (Groq/OpenAI), fallback to local DB.
        """
        import os
        import json
        import requests

        prompt = (
            f"Generate 2 to 3 practical kitchen substitutions for {quantity} {unit} of '{ingredient}'.\n"
            "CRITICAL: You MUST ALWAYS return at least 2 substitutes, even for basic ingredients like sugar (brown sugar, honey), salt (sea salt, soy sauce), flour (whole wheat), milk (plant milk, water+butter).\n"
            "NEVER say 'no substitute' or 'no direct substitute'. "
            "If the ingredient is obscure, explicitly categorize it (e.g., cheeses, meats, vegetables, dairy, pantry staples, spices) "
            "and suggest the closest matching alternative from that category.\n"
            "Return ONLY a valid JSON array of objects securely matching this exact format:\n"
            "[\n"
            "  {\n"
            "    \"name\": \"substitute name (e.g., generic categorical alternative)\",\n"
            "    \"ratio\": \"e.g., use 1:1\",\n"
            "    \"note\": \"brief cooking tip or category justification\"\n"
            "  }\n"
            "]\n"
            "Do NOT wrap in markdown blocks, no backticks, no explanation - raw JSON ONLY."
        )

        messages = [
            {"role": "system", "content": "You are a culinary expert API. Respond ONLY with valid JSON array of objects. No intro text."},
            {"role": "user", "content": prompt}
        ]

        groq_key = os.getenv("GROQ_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")

        response_text = ""
        try:
            if groq_key:
                resp = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    json={"model": "llama3-8b-8192", "messages": messages, "temperature": 0.4},
                    headers={"Authorization": f"Bearer {groq_key}"},
                    timeout=10
                )
                if resp.status_code == 200:
                    response_text = resp.json()["choices"][0]["message"]["content"]
                    
            elif openai_key:
                resp = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    json={"model": "gpt-3.5-turbo", "messages": messages, "temperature": 0.4},
                    headers={"Authorization": f"Bearer {openai_key}"},
                    timeout=10
                )
                if resp.status_code == 200:
                    response_text = resp.json()["choices"][0]["message"]["content"]

            if response_text:
                logger.info(f"Raw AI response: {response_text}")
                
                # Strip markdown code blocks if present
                clean_text = response_text.strip()
                if clean_text.startswith("```json"):
                    clean_text = clean_text[7:]
                elif clean_text.startswith("```"):
                    clean_text = clean_text[3:]
                    
                if clean_text.endswith("```"):
                    clean_text = clean_text[:-3]
                    
                clean_text = clean_text.strip()
                
                start = clean_text.find('[')
                end = clean_text.rfind(']') + 1
                if start >= 0 and end > start:
                    try:
                        return json.loads(clean_text[start:end])
                    except json.JSONDecodeError as json_err:
                        logger.error(f"JSON parsing failed. Error: {json_err}. Clean Text: {clean_text}")

            return self._fallback_suggest(ingredient, quantity, unit, available_ingredients)
        except Exception as e:
            logger.error(f"AI substitution error: {e}")
            return self._fallback_suggest(ingredient, quantity, unit, available_ingredients)

    def _fallback_suggest(
        self,
        ingredient: str,
        quantity: float,
        unit: str,
        available_ingredients: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Fallback rule-based and category substitutions"""
        ingredient_lower = ingredient.lower()
        
        # 1. Direct DB matches
        matches = []
        for key, subs in self.substitutions.items():
            if key in ingredient_lower or ingredient_lower in key:
                matches.extend(subs)
        
        if not matches:
            for key, subs in self.substitutions.items():
                if any(word in ingredient_lower for word in key.split()):
                    matches.extend(subs)
        
        # 2. Category-based dynamic fallback
        if not matches:
            cat_match = "generic pantry staple"
            if any(c in ingredient_lower for c in ["cheese", "cheddar", "mozzarella", "parmesan", "brie", "gouda"]):
                cat_match = "mild melting or grating cheese"
            elif any(m in ingredient_lower for m in ["chicken", "beef", "pork", "meat", "lamb", "turkey"]):
                cat_match = "tofu, beans, or another mild protein"
            elif any(v in ingredient_lower for v in ["carrot", "onion", "broccoli", "potato", "vegetable"]):
                cat_match = "similar textured root or cruciferous vegetable"
            elif any(d in ingredient_lower for d in ["milk", "cream", "butter", "dairy", "yogurt"]):
                cat_match = "dairy-free milk alternative (like almond/oat milk)"
            elif any(s in ingredient_lower for s in ["green chilli", "red chilli", "chili", "jalapeno", "pepper", "paprika"]):
                cat_match = "another mild or hot pepper/spice"
            elif any(s in ingredient_lower for s in ["cumin", "salt", "sugar", "spice", "herb", "coriander", "turmeric", "masala"]):
                cat_match = "another earth-toned spice or herb"

            return [
                {
                    "name": cat_match,
                    "ratio": "1:1",
                    "note": f"Categorical replacement for {ingredient}"
                },
                {
                    "name": "omit ingredient if non-essential",
                    "ratio": "N/A",
                    "note": "Optional culinary adjustment"
                }
            ]
        
        # Calculate adjusted quantities and map to new JSON format
        results = []
        for match in matches:
            ratio_str = match.get("ratio", "1:1")
            results.append({
                "name": match["name"],
                "ratio": f"use {ratio_str}",
                "note": match.get("note", "Standard substitute"),
            })
        
        return results[:3]

# Global service instance
ai_substitution_service = AISubstitutionService()
