"""
Nutritional analysis service
Integrates with nutrition APIs to calculate calories, protein, carbs, and fat
Adjusts dynamically based on scaling changes
"""

import logging
from typing import Dict, List, Any, Optional
import httpx

logger = logging.getLogger(__name__)

# Nutrition database (fallback when API unavailable)
NUTRITION_DATABASE = {
    "chicken breast": {"calories": 165, "protein": 31, "carbs": 0, "fat": 3.6, "unit": "100g"},
    "beef": {"calories": 250, "protein": 26, "carbs": 0, "fat": 15, "unit": "100g"},
    "salmon": {"calories": 206, "protein": 22, "carbs": 0, "fat": 13, "unit": "100g"},
    "egg": {"calories": 155, "protein": 13, "carbs": 1.1, "fat": 11, "unit": "100g"},
    "milk": {"calories": 61, "protein": 3.2, "carbs": 4.8, "fat": 3.3, "unit": "100ml"},
    "butter": {"calories": 717, "protein": 0.9, "carbs": 0.06, "fat": 81, "unit": "100g"},
    "olive oil": {"calories": 884, "protein": 0, "carbs": 0, "fat": 100, "unit": "100ml"},
    "flour": {"calories": 364, "protein": 10, "carbs": 77, "fat": 1, "unit": "100g"},
    "sugar": {"calories": 387, "protein": 0, "carbs": 100, "fat": 0, "unit": "100g"},
    "salt": {"calories": 0, "protein": 0, "carbs": 0, "fat": 0, "unit": "100g"},
    "cheese": {"calories": 402, "protein": 25, "carbs": 1.3, "fat": 33, "unit": "100g"},
    "tomato": {"calories": 18, "protein": 0.9, "carbs": 3.9, "fat": 0.2, "unit": "100g"},
    "carrot": {"calories": 41, "protein": 0.9, "carbs": 10, "fat": 0.2, "unit": "100g"},
    "onion": {"calories": 40, "protein": 1.1, "carbs": 9, "fat": 0.1, "unit": "100g"},
    "garlic": {"calories": 149, "protein": 6.4, "carbs": 33, "fat": 0.5, "unit": "100g"},
    "rice": {"calories": 130, "protein": 2.7, "carbs": 28, "fat": 0.3, "unit": "100g"},
    "pasta": {"calories": 131, "protein": 5, "carbs": 25, "fat": 1.1, "unit": "100g"},
    "bread": {"calories": 265, "protein": 9, "carbs": 49, "fat": 3.3, "unit": "100g"},
    "honey": {"calories": 304, "protein": 0.3, "carbs": 82, "fat": 0, "unit": "100g"},
    "yogurt": {"calories": 59, "protein": 3.5, "carbs": 4.7, "fat": 0.4, "unit": "100g"},
}

class NutritionService:
    """Service for nutritional analysis"""
    
    def __init__(self):
        self.nutrition_db = NUTRITION_DATABASE
        self.usda_api_key = None  # Set from environment if available
    
    def get_nutrition_info(self, ingredient: str, quantity: float, unit: str) -> Optional[Dict[str, Any]]:
        """
        Get nutrition information for an ingredient
        
        Args:
            ingredient: Ingredient name
            quantity: Quantity of ingredient
            unit: Unit of measurement
        
        Returns:
            Dictionary with nutritional values scaled to the quantity
        """
        ingredient_lower = ingredient.lower().strip()
        
        # Try exact match first
        if ingredient_lower in self.nutrition_db:
            nutrition = self.nutrition_db[ingredient_lower].copy()
            return self._scale_nutrition(nutrition, quantity, unit)
        
        # Try partial match
        for key, nutrition in self.nutrition_db.items():
            if key in ingredient_lower or ingredient_lower in key:
                nutrition = nutrition.copy()
                return self._scale_nutrition(nutrition, quantity, unit)
        
        # Try API (if configured)
        try:
            nutrition = self._fetch_from_api(ingredient)
            if nutrition:
                return self._scale_nutrition(nutrition, quantity, unit)
        except Exception as e:
            logger.warning(f"Could not fetch nutrition from API: {e}")
        
        # No data found
        return None
    
    def _scale_nutrition(self, nutrition: Dict[str, float], quantity: float, unit: str) -> Dict[str, float]:
        """Scale nutrition information based on quantity and unit"""
        # Parse unit to base unit
        base_quantity = self._convert_to_base_unit(quantity, unit)
        
        # Get the reference quantity from nutrition data
        ref_unit = nutrition.get("unit", "100g")
        ref_quantity = self._convert_to_base_unit(100, "g" if "g" in ref_unit else "ml")
        
        # Calculate scaling factor
        scaling_factor = base_quantity / ref_quantity
        
        # Scale all macronutrients
        return {
            "ingredient": nutrition.get("ingredient", ""),
            "calories": round(nutrition["calories"] * scaling_factor, 1),
            "protein": round(nutrition["protein"] * scaling_factor, 1),
            "carbs": round(nutrition["carbs"] * scaling_factor, 1),
            "fat": round(nutrition["fat"] * scaling_factor, 1),
            "quantity": quantity,
            "unit": unit,
        }
    
    def _convert_to_base_unit(self, quantity: float, unit: str) -> float:
        """Convert any unit to grams or ml"""
        unit_lower = unit.lower().strip()
        
        conversions = {
            "g": 1,
            "gram": 1,
            "kg": 1000,
            "oz": 28.35,
            "ounce": 28.35,
            "lb": 453.592,
            "pound": 453.592,
            "ml": 1,
            "l": 1000,
            "liter": 1000,
            "tsp": 5,
            "teaspoon": 5,
            "tbsp": 15,
            "tablespoon": 15,
            "cup": 240,
        }
        
        if unit_lower in conversions:
            return quantity * conversions[unit_lower]
        
        return quantity  # Default no conversion
    
    def _fetch_from_api(self, ingredient: str) -> Optional[Dict[str, Any]]:
        """Fetch nutrition info from external API"""
        # Placeholder for API integration
        # Could integrate with USDA FoodData Central, Nutritionix, etc.
        return None
    
    def analyze_recipe_nutrition(self, ingredients: List[Dict[str, Any]], servings: int = 1) -> Dict[str, Any]:
        """
        Analyze total nutrition for a complete recipe
        
        Args:
            ingredients: List of ingredients with quantity and unit
            servings: Number of servings
        
        Returns:
            Total nutrition information per serving and total
        """
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        
        ingredient_nutrition = []
        
        for ing in ingredients:
            name = ing.get("name", "")
            quantity = ing.get("quantity", 0)
            unit = ing.get("unit", "g")
            
            nutrition = self.get_nutrition_info(name, quantity, unit)
            if nutrition:
                ingredient_nutrition.append({
                    "ingredient": name,
                    "nutrition": nutrition,
                })
                total_calories += nutrition["calories"]
                total_protein += nutrition["protein"]
                total_carbs += nutrition["carbs"]
                total_fat += nutrition["fat"]
        
        return {
            "total": {
                "calories": round(total_calories, 1),
                "protein": round(total_protein, 1),
                "carbs": round(total_carbs, 1),
                "fat": round(total_fat, 1),
            },
            "per_serving": {
                "calories": round(total_calories / servings, 1),
                "protein": round(total_protein / servings, 1),
                "carbs": round(total_carbs / servings, 1),
                "fat": round(total_fat / servings, 1),
            },
            "ingredients": ingredient_nutrition,
            "servings": servings,
        }
    
    def scale_nutrition(
        self,
        original_nutrition: Dict[str, float],
        scaling_factor: float
    ) -> Dict[str, float]:
        """
        Adjust nutrition information when recipe is scaled
        
        Args:
            original_nutrition: Original nutrition data
            scaling_factor: Scaling factor (e.g., 0.5 for half recipe, 2 for double)
        
        Returns:
            Scaled nutrition data
        """
        return {
            "calories": round(original_nutrition["calories"] * scaling_factor, 1),
            "protein": round(original_nutrition["protein"] * scaling_factor, 1),
            "carbs": round(original_nutrition["carbs"] * scaling_factor, 1),
            "fat": round(original_nutrition["fat"] * scaling_factor, 1),
            "scaling_factor": scaling_factor,
        }
    
    def get_macros_percentage(self, nutrition: Dict[str, float]) -> Dict[str, float]:
        """Calculate percentage of calories from each macronutrient"""
        total_cals = nutrition.get("calories", 0)
        if total_cals == 0:
            return {"protein": 0, "carbs": 0, "fat": 0}
        
        protein_cals = nutrition.get("protein", 0) * 4
        carbs_cals = nutrition.get("carbs", 0) * 4
        fat_cals = nutrition.get("fat", 0) * 9
        
        return {
            "protein_percent": round((protein_cals / total_cals) * 100, 1),
            "carbs_percent": round((carbs_cals / total_cals) * 100, 1),
            "fat_percent": round((fat_cals / total_cals) * 100, 1),
        }

# Global service instance
nutrition_service = NutritionService()
