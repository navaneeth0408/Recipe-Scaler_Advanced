"""
AI-powered ingredient substitution endpoint.

Returns structured substitutions focusing on availability and practicality.
"""

from fastapi import APIRouter, HTTPException
from app.models.schemas import SubstituteRequest, SubstituteResponse
from app.services.ai_substitution_service import ai_substitution_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api")

@router.post(
    "/substitute",
    response_model=SubstituteResponse,
    tags=["ingredients", "ai"],
)
async def get_substitutions(data: SubstituteRequest) -> SubstituteResponse:
    """
    Generate structured ingredient substitution suggestions for a single ingredient.
    """
    ingredient = (data.ingredient or "").strip()
    if not ingredient:
        raise HTTPException(status_code=400, detail="Ingredient must not be empty")
    if data.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0")
        
    logger.info(f"Generating typical household substitutions for {data.quantity} {data.unit} of {ingredient}")
    
    # Generate substitutions using the updated ai_substitution_service
    substitutions = ai_substitution_service.suggest_substitutions(
        ingredient,
        data.quantity,
        data.unit or ""
    )
    
    return SubstituteResponse(
        substitutes=substitutions
    )
