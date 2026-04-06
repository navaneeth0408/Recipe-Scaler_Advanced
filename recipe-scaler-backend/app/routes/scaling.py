"""
Route handlers for recipe scaling operations
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import logging

from app.models.schemas import (
    ScalingRequest,
    ScaledIngredientsResponse,
    Ingredient,
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
    Scale recipe ingredients based on serving size change.
    Accepts { ingredients, value, type } from the frontend UI
    or { ingredients, original_servings, target_servings } from direct API use.
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

        scale_factor = targ / orig

        scaled_ingredients = []
        for ing in request.ingredients:
            # Parse the raw quantity string from the ingredient display text if needed.
            # The ingredient object may have quantity as a float already, or as a
            # string like "1/3" (from display text parsed by the frontend).
            raw_qty = ing.quantity
            try:
                qty = ScalingService.parse_fraction(raw_qty)
            except Exception:
                qty = 1.0

            new_qty = qty * scale_factor
            new_qty_rounded = ScalingService._round_quantity(new_qty)

            scaled_ingredients.append(
                Ingredient(
                    name=ing.name,
                    quantity=new_qty_rounded,
                    unit=ing.unit or "",
                    original_quantity=qty,
                    original_unit=ing.unit or "",
                    notes=ing.notes,
                )
            )

        return ScaledIngredientsResponse(
            original_servings=orig,
            target_servings=targ,
            scale_factor=scale_factor,
            ingredients=scaled_ingredients,
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
    try:
        if quantity < 0:
            raise ValueError("Quantity must be non-negative")
        converted = ScalingService.convert_unit(quantity, from_unit, to_unit)
        return {'quantity': quantity, 'from_unit': from_unit, 'to_unit': to_unit,
                'converted_quantity': converted, 'success': True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scaling/suggest-unit")
def suggest_unit_conversion(
    quantity: float,
    current_unit: str,
    db: Session = Depends(get_db)
):
    try:
        if quantity < 0:
            raise ValueError("Quantity must be non-negative")
        suggested_qty, suggested_unit = ScalingService.suggest_unit_conversion(quantity, current_unit)
        return {'current_quantity': quantity, 'current_unit': current_unit,
                'suggested_quantity': suggested_qty, 'suggested_unit': suggested_unit,
                'changed': (suggested_unit != current_unit), 'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
