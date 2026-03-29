"""
Route handlers for recipe scaling operations
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import logging

from app.models.schemas import (
    ScalingRequest,
    ScaledIngredientsResponse,
)
from app.services.scaling_service import ScalingService
from app.database.db import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["scaling"])


@router.post("/scale", response_model=ScaledIngredientsResponse)
def scale_ingredients(
    request: ScalingRequest,
    db: Session = Depends(get_db)
):
    """
    Scale recipe ingredients based on serving size change
    
    Takes original servings and target servings, returns scaled ingredient list.
    
    Example request:
    ```json
    {
        "ingredients": [
            {
                "name": "flour",
                "quantity": 2.0,
                "unit": "cup"
            }
        ],
        "original_servings": 4,
        "target_servings": 8
    }
    ```
    
    Response will show the 2 cups flour scaled to 4 cups (2x scale factor).
    """
    try:
        orig = request.original_servings if request.original_servings is not None else 1.0
        targ = request.target_servings if request.target_servings is not None else request.value
        
        if targ is None:
            targ = orig
            
        if orig <= 0 or targ <= 0:
            raise ValueError("Servings must be greater than 0")

        if not request.ingredients:
            return ScaledIngredientsResponse(
                original_servings=orig,
                target_servings=targ,
                scale_factor=targ / orig,
                ingredients=[],
                success=True
            )

        # Convert Pydantic models to dicts
        ingredients_dict = [ing.model_dump() for ing in request.ingredients]

        # Scale ingredients
        scaled_ingredients, scale_factor = ScalingService.scale_ingredients(
            ingredients_dict,
            orig,
            targ
        )

        return ScaledIngredientsResponse(
            original_servings=orig,
            target_servings=targ,
            scale_factor=scale_factor,
            ingredients=[
                type(request.ingredients[0])(**ing)
                for ing in scaled_ingredients
            ],
            success=True
        )

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error scaling ingredients: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scaling/convert-unit")
def convert_unit(
    quantity: float,
    from_unit: str,
    to_unit: str,
    db: Session = Depends(get_db)
):
    """
    Convert ingredient quantity from one unit to another
    
    Query parameters:
    - quantity: Amount to convert
    - from_unit: Source unit (cup, tbsp, tsp, gram, ounce, etc)
    - to_unit: Target unit
    
    Example:
    GET /api/scaling/convert-unit?quantity=16&from_unit=tablespoon&to_unit=cup
    
    Returns: 1.0 cup
    """
    try:
        if quantity < 0:
            raise ValueError("Quantity must be non-negative")

        converted = ScalingService.convert_unit(quantity, from_unit, to_unit)

        return {
            'quantity': quantity,
            'from_unit': from_unit,
            'to_unit': to_unit,
            'converted_quantity': converted,
            'success': True,
        }

    except ValueError as e:
        logger.error(f"Unit conversion error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error converting unit: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scaling/suggest-unit")
def suggest_unit_conversion(
    quantity: float,
    current_unit: str,
    db: Session = Depends(get_db)
):
    """
    Suggest a more convenient unit for the given quantity
    
    Example:
    GET /api/scaling/suggest-unit?quantity=8&current_unit=teaspoon
    
    Returns: 2 tablespoons (more convenient than 8 teaspoons)
    """
    try:
        if quantity < 0:
            raise ValueError("Quantity must be non-negative")

        suggested_qty, suggested_unit = ScalingService.suggest_unit_conversion(
            quantity,
            current_unit
        )

        return {
            'current_quantity': quantity,
            'current_unit': current_unit,
            'suggested_quantity': suggested_qty,
            'suggested_unit': suggested_unit,
            'changed': (suggested_unit != current_unit),
            'success': True,
        }

    except Exception as e:
        logger.error(f"Error suggesting unit: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
