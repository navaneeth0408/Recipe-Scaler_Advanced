"""
Recipe scaling service
Handles scaling ingredients based on serving size changes
"""

from typing import List, Dict, Tuple
import logging
import re

logger = logging.getLogger(__name__)


class ScalingService:
    """Service for scaling recipes based on servings"""

    # Unit conversion tables
    # Base unit: grams for weight, milliliters for volume
    CONVERSIONS = {
        'weight': {
            'ounce': 28.35,  # 1 oz = 28.35g
            'gram': 1.0,
            'kilogram': 1000.0,
            'pound': 453.592,  # 1 lb = 453.592g
        },
        'volume': {
            'teaspoon': 4.929,  # 1 tsp = 4.929 ml
            'tablespoon': 14.787,  # 1 tbsp = 14.787 ml
            'cup': 236.588,  # 1 cup = 236.588 ml
            'milliliter': 1.0,
            'liter': 1000.0,
        }
    }

    # Unit categories
    UNIT_CATEGORIES = {
        'weight': ['ounce', 'gram', 'kilogram', 'pound'],
        'volume': ['teaspoon', 'tablespoon', 'cup', 'milliliter', 'liter'],
        'count': ['whole', 'pinch', 'dash'],
    }

    @staticmethod
    def parse_fraction(value):
        if isinstance(value, (int, float)):
            return float(value)
        value = str(value).strip()
        if not value:
            return 0.0
        try:
            if " " in value:
                whole, frac = value.split(" ")
                num, den = frac.split("/")
                return float(whole) + float(num)/float(den)
            if "/" in value:
                num, den = value.split("/")
                return float(num)/float(den)
            return float(value)
        except Exception:
            # If it's a non-numeric string that isn't empty, 1.0 is a safer default than 0.0
            return 1.0 if value else 0.0

    @staticmethod
    def scale_ingredient(
        ingredient: Dict,
        original_servings: float,
        target_servings: float
    ) -> Dict:
        """
        Scale a single ingredient based on serving change
        """
        if original_servings <= 0:
            logger.warning("Original servings must be positive")
            return ingredient

        scale_factor = target_servings / original_servings
        
        # Get raw quantity
        raw_qty = ingredient.get('quantity', 0)
        unit = (ingredient.get('unit') or '').lower().strip()
        
        # Check if it's a non-numeric/vague quantity (like "sprinkle", "pinch", "to taste")
        # OR if the unit itself is vague (like "handful", "pinch")
        # Vague units should generally not be scaled per user request
        vague_units = ['pinch', 'handful', 'sprinkle', 'dash', 'drop', 'to taste']
        
        is_vague = False
        if any(v in unit for v in vague_units):
            is_vague = True
            new_quantity = raw_qty
        elif isinstance(raw_qty, str):
            # If it's empty, treat as 1.0 (internal logic often defaults empty to 1)
            if not raw_qty.strip():
                qty = 1.0
            # If it contains digits/fractions, it's numeric
            elif re.search(r'\d', raw_qty):
                qty = ScalingService.parse_fraction(raw_qty)
            # Otherwise it's a vague string like "pinch", "sprinkle", "to taste"
            else:
                is_vague = True
                new_quantity = raw_qty
        else:
            qty = float(raw_qty) if raw_qty is not None else 0.0

        if not is_vague:
            new_quantity = ScalingService._round_quantity(qty * scale_factor)

        # Create scaled ingredient copy
        scaled = ingredient.copy()
        scaled['quantity'] = new_quantity
        scaled['original_quantity'] = raw_qty
        scaled['original_unit'] = ingredient.get('unit')

        return scaled

    @staticmethod
    def scale_ingredients(
        ingredients: List[Dict],
        original_servings: float,
        target_servings: float
    ) -> Tuple[List[Dict], float]:
        """
        Scale multiple ingredients
        
        Args:
            ingredients: List of ingredient dicts
            original_servings: Original recipe servings
            target_servings: Target recipe servings
            
        Returns:
            (scaled_ingredients, scale_factor)
        """
        if original_servings <= 0:
            raise ValueError("Original servings must be positive")

        scale_factor = target_servings / original_servings
        scaled_ingredients = []

        for ingredient in ingredients:
            scaled = ScalingService.scale_ingredient(
                ingredient,
                original_servings,
                target_servings
            )
            scaled_ingredients.append(scaled)

        return scaled_ingredients, scale_factor

    @staticmethod
    def _round_quantity(quantity: float) -> float:
        """
        Round quantity to a reasonable precision
        
        Common cooking measurements often use fractions like 1/4, 1/3, 1/2
        This function rounds to reasonable values
        """
        if quantity == 0:
            return 0

        # Define common fractions and their decimal values
        common_fractions = [
            (0.125, 0.125),  # 1/8
            (0.167, 0.167),  # 1/6
            (0.25, 0.25),    # 1/4
            (0.333, 0.333),  # 1/3
            (0.5, 0.5),      # 1/2
            (0.667, 0.667),  # 2/3
            (0.75, 0.75),    # 3/4
        ]

        # For whole numbers and large quantities, round to nearest 0.5
        if quantity >= 5:
            return round(quantity * 2) / 2

        # For quantities < 5, try to match common fractions
        for fraction_val, fraction_tol in common_fractions:
            if abs(quantity - fraction_val) < 0.05:
                return fraction_val

        # For other values, round to 2 decimal places
        return round(quantity, 2)

    @staticmethod
    def convert_unit(
        quantity: float,
        from_unit: str,
        to_unit: str
    ) -> float:
        """
        Convert quantity from one unit to another
        
        Args:
            quantity: Amount to convert
            from_unit: Source unit
            to_unit: Target unit
            
        Returns:
            Converted quantity
            
        Raises:
            ValueError: If units can't be converted
        """
        if from_unit == to_unit:
            return quantity

        # Find unit categories
        from_category = None
        to_category = None

        for category, units in ScalingService.UNIT_CATEGORIES.items():
            if from_unit in units:
                from_category = category
            if to_unit in units:
                to_category = category

        if from_category != to_category:
            raise ValueError(
                f"Cannot convert {from_unit} to {to_unit} - incompatible unit types"
            )

        if from_category == 'count':
            raise ValueError(
                f"Cannot convert count-based units ({from_unit} to {to_unit})"
            )

        # Get conversion factors
        conversions = ScalingService.CONVERSIONS[from_category]

        if from_unit not in conversions or to_unit not in conversions:
            raise ValueError(f"Unsupported units: {from_unit} or {to_unit}")

        # Convert to base unit, then to target unit
        base_value = quantity * conversions[from_unit]
        target_value = base_value / conversions[to_unit]

        return target_value

    @staticmethod
    def suggest_unit_conversion(quantity: float, current_unit: str) -> Tuple[float, str]:
        """
        Suggest a more convenient unit for the given quantity
        
        Example: 8 teaspoons -> 2 tablespoons
        """
        if current_unit == 'whole' or current_unit == 'pinch' or current_unit == 'dash':
            return quantity, current_unit

        # Find category
        category = None
        for cat, units in ScalingService.UNIT_CATEGORIES.items():
            if current_unit in units:
                category = cat
                break

        if category == 'count':
            return quantity, current_unit

        # For volume units, suggest conversions
        if category == 'volume':
            # If teaspoons >= 3, suggest tablespoons
            if current_unit == 'teaspoon' and quantity >= 3:
                new_quantity = ScalingService.convert_unit(quantity, 'teaspoon', 'tablespoon')
                return ScalingService._round_quantity(new_quantity), 'tablespoon'

            # If tablespoons >= 16, suggest cups
            if current_unit == 'tablespoon' and quantity >= 16:
                new_quantity = ScalingService.convert_unit(quantity, 'tablespoon', 'cup')
                return ScalingService._round_quantity(new_quantity), 'cup'

            # If milliliters >= 240, suggest cups
            if current_unit == 'milliliter' and quantity >= 240:
                new_quantity = ScalingService.convert_unit(quantity, 'milliliter', 'cup')
                return ScalingService._round_quantity(new_quantity), 'cup'

        # For weight units, suggest conversions
        if category == 'weight':
            # If grams >= 453, suggest pounds
            if current_unit == 'gram' and quantity >= 453:
                new_quantity = ScalingService.convert_unit(quantity, 'gram', 'pound')
                return ScalingService._round_quantity(new_quantity), 'pound'

            # If ounces >= 16, suggest pounds
            if current_unit == 'ounce' and quantity >= 16:
                new_quantity = ScalingService.convert_unit(quantity, 'ounce', 'pound')
                return ScalingService._round_quantity(new_quantity), 'pound'

        return quantity, current_unit

    @staticmethod
    def get_scale_factor_string(original_servings: float, target_servings: float) -> str:
        """Get human-readable scale factor description"""
        factor = target_servings / original_servings

        if factor == 2:
            return "doubled"
        elif factor == 0.5:
            return "halved"
        elif factor == 3:
            return "tripled"
        else:
            return f"scaled by {factor:.2f}x"
