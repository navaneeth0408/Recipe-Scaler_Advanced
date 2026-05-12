"""
AI-powered ingredient substitution service
Suggests alternatives based on availability, categories, and practical cooking replacements.
"""

import logging
import difflib
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
    ],
    "paneer": [
        {
            "name": "firm tofu",
            "ratio": "1:1",
            "ratio_float": 1.0,
            "note": "Excellent dairy-free and vegan alternative"
        },
        {
            "name": "halloumi",
            "ratio": "1:1",
            "ratio_float": 1.0,
            "note": "Similar grilling and non-melting texture"
        }
    ],
    "coconut milk": [
        {
            "name": "almond milk",
            "ratio": "1:1",
            "ratio_float": 1.0,
            "note": "Much thinner, mild flavor"
        },
        {
            "name": "heavy cream + water",
            "ratio": "1:1",
            "ratio_float": 1.0,
            "note": "Dairy alternative with similar richness"
        }
    ],
    "coriander powder": [
        {
            "name": "cumin powder",
            "ratio": "1:1",
            "ratio_float": 1.0,
            "note": "Different flavor profile but works well in curries"
        },
        {
            "name": "garam masala",
            "ratio": "1:2",
            "ratio_float": 0.5,
            "note": "Use half as it's much stronger"
        }
    ],
    "ghee": [
        {
            "name": "butter",
            "ratio": "1:1",
            "ratio_float": 1.0,
            "note": "Clarified butter (ghee) is just butter with milk solids removed"
        },
        {
            "name": "vegetable oil",
            "ratio": "1:1",
            "ratio_float": 1.0,
            "note": "Any neutral oil works for high-heat cooking"
        }
    ],
    "lemon": [
        {
            "name": "lime",
            "ratio": "1:1",
            "ratio_float": 1.0,
            "note": "Direct citrus replacement"
        },
        {
            "name": "white vinegar",
            "ratio": "1/2",
            "ratio_float": 0.5,
            "note": "For acidity without the citrus flavor"
        }
    ],
    "meat masala": [
        {
            "name": "garam masala + 1 tsp chilli powder",
            "ratio": "1:1",
            "ratio_float": 1.0,
            "note": "Replicates the spice blend's profile"
        },
        {
            "name": "curry powder",
            "ratio": "1:1",
            "ratio_float": 1.0,
            "note": "General all-purpose Indian spice blend"
        }
    ],
    "curry leaves": [
        {
            "name": "bay leaf",
            "ratio": "2:1",
            "ratio_float": 2.0,
            "note": "Similar herbal undertones but lacks the distinct aroma"
        }
    ],
    "mustard seeds": [
        {
            "name": "cumin seeds",
            "ratio": "1:1",
            "ratio_float": 1.0,
            "note": "For tempering (tadka), though flavor is different"
        }
    ],
    "rice": [
        {
            "name": "cauliflower rice",
            "ratio": "1:1",
            "ratio_float": 1.0,
            "note": "Low-carb alternative"
        },
        {
            "name": "quinoa",
            "ratio": "1:1",
            "ratio_float": 1.0,
            "note": "Similar texture and protein-rich"
        }
    ],
    "flour": [
        {
            "name": "whole wheat flour",
            "ratio": "1:1",
            "ratio_float": 1.0,
            "note": "Healthier alternative, may need more liquid"
        }
    ]
}

class AISubstitutionService:
    """Service for AI-powered ingredient substitution"""
    
    def __init__(self):
        self.substitutions = SUBSTITUTIONS
        self.dataset_substitutions = {}
        self._load_dataset_subs()

    def _load_dataset_subs(self):
        """Load the pre-processed Kaggle substitution dataset if available."""
        import os
        import json
        try:
            data_file = os.path.join(os.path.dirname(__file__), "..", "data", "dataset_substitutions.json")
            if os.path.exists(data_file):
                with open(data_file, 'r') as f:
                    self.dataset_substitutions = json.load(f)
                logger.info(f"Loaded {len(self.dataset_substitutions)} ingredients from Kaggle dataset.")
        except Exception as e:
            logger.error(f"Failed to load substitution dataset: {e}")
    
    def suggest_substitutions(
        self,
        ingredient: str,
        quantity: float,
        unit: str,
        available_ingredients: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Suggest ingredient substitutions based on AI model (Groq/OpenAI), fallback to local DB and Kaggle dataset.
        """
        ingredient_lower = ingredient.lower().strip()
        
        # 1. Check local manual database first (high confidence)
        matches = []
        if ingredient_lower in self.substitutions:
            for sub in self.substitutions[ingredient_lower]:
                matches.append({
                    "name": sub["name"],
                    "ratio": f"use {sub.get('ratio', '1:1')}",
                    "note": sub.get("note", "Standard substitute")
                })

        # 2. Check Kaggle Dataset (broader knowledge)
        if len(matches) < 2 and ingredient_lower in self.dataset_substitutions:
            for sub_name in self.dataset_substitutions[ingredient_lower]:
                # Avoid duplicates
                if any(m['name'].lower() == sub_name.lower() for m in matches):
                    continue
                matches.append({
                    "name": sub_name,
                    "ratio": "use 1:1",
                    "note": "Dataset-suggested alternative"
                })
                if len(matches) >= 3:
                    break

                if len(matches) >= 3:
                    break

        # 3. Fuzzy matching for local DB and Dataset
        if len(matches) < 2:
            # Check for close matches in local DB keys
            close_matches = difflib.get_close_matches(ingredient_lower, self.substitutions.keys(), n=2, cutoff=0.55)
            for cm in close_matches:
                if cm == ingredient_lower: continue # Already checked
                for sub in self.substitutions[cm]:
                    if any(m['name'].lower() == sub['name'].lower() for m in matches): continue
                    matches.append({
                        "name": sub["name"],
                        "ratio": f"use {sub.get('ratio', '1:1')}",
                        "note": f"Substitute for {cm} (similar to {ingredient})"
                    })
            
            # Check for close matches in Dataset keys
            if len(matches) < 3:
                dataset_close = difflib.get_close_matches(ingredient_lower, self.dataset_substitutions.keys(), n=2, cutoff=0.6)
                for dc in dataset_close:
                    if dc == ingredient_lower: continue
                    for sub_name in self.dataset_substitutions[dc]:
                        if any(m['name'].lower() == sub_name.lower() for m in matches): continue
                        matches.append({
                            "name": sub_name,
                            "ratio": "use 1:1",
                            "note": f"Alternative for {dc}"
                        })
                        if len(matches) >= 3: break

        if matches:
            # Filter out self-substitution
            filtered_matches = [m for m in matches if m["name"].lower() != ingredient_lower]
            if filtered_matches:
                return filtered_matches[:3]

        # 3. Fallback to AI then rule-based logic
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
                        ai_subs = json.loads(clean_text[start:end])
                        # Filter out self-substitution from AI results
                        filtered_ai = [s for s in ai_subs if s.get("name", "").lower() != ingredient_lower]
                        if filtered_ai:
                            return filtered_ai
                        # If AI only returned self-substitution, fall back
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
            if any(s in ingredient_lower for s in ["cumin", "salt", "sugar", "spice", "herb", "coriander", "turmeric", "masala", "powder"]):
                cat_match = "another compatible spice or spice blend"
            elif any(d in ingredient_lower for d in ["milk", "cream", "butter", "dairy", "yogurt", "ghee"]):
                cat_match = "another fat or dairy alternative (like oil or plant milk)"
            elif any(c in ingredient_lower for c in ["cheese", "cheddar", "mozzarella", "parmesan", "brie", "gouda"]):
                cat_match = "mild melting or grating cheese"
            elif any(m in ingredient_lower for m in ["chicken", "beef", "pork", "meat", "lamb", "turkey"]):
                # Ensure it's not a masala/spice match first
                cat_match = "tofu, beans, or another mild protein"
            elif any(v in ingredient_lower for v in ["carrot", "onion", "broccoli", "potato", "vegetable"]):
                cat_match = "similar textured root or cruciferous vegetable"
            elif any(s in ingredient_lower for s in ["green chilli", "red chilli", "chili", "jalapeno", "pepper", "paprika"]):
                cat_match = "another mild or hot pepper/spice"
            elif any(l in ingredient_lower for l in ["lemon", "lime", "citrus", "vinegar"]):
                cat_match = "another acidic ingredient like lime or vinegar"
            elif any(f in ingredient_lower for f in ["flour", "maida", "powder"]):
                cat_match = "any all-purpose or whole wheat flour"
            elif any(r in ingredient_lower for r in ["rice", "grain", "poha"]):
                cat_match = "any available rice or cereal grain"

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
            if match["name"].lower() == ingredient_lower:
                continue
            ratio_str = match.get("ratio", "1:1")
            results.append({
                "name": match["name"],
                "ratio": f"use {ratio_str}",
                "note": match.get("note", "Standard substitute"),
            })
        
        return results[:3]

# Global service instance
ai_substitution_service = AISubstitutionService()
