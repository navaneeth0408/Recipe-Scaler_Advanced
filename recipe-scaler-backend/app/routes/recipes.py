"""
Route handlers for recipe persistence operations
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
import logging

from app.models.schemas import (
    RecipeCreate,
    Recipe,
    RecipeResponse,
    RecipesListResponse,
    Ingredient,
)
from app.database.db import get_db, RecipeDB, IngredientDB
from app.services.ingredient_service import IngredientService
from app.services.scaling_service import ScalingService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/recipes", tags=["recipes"])


def _ingredient_to_model(ing_db: IngredientDB) -> Ingredient:
    """Convert database ingredient to Pydantic model"""
    return Ingredient(
        name=ing_db.name,
        quantity=ing_db.quantity,
        unit=ing_db.unit,
        original_quantity=ing_db.original_quantity,
        original_unit=ing_db.original_unit,
        notes=ing_db.notes,
    )


def _recipe_db_to_model(recipe_db: RecipeDB) -> Recipe:
    """Convert database recipe to Pydantic model"""
    return Recipe(
        id=recipe_db.id,
        name=recipe_db.name,
        ingredients=[_ingredient_to_model(ing) for ing in recipe_db.ingredients],
        servings=recipe_db.servings,
        source=recipe_db.source,
        source_url=recipe_db.source_url,
        notes=recipe_db.notes,
        instructions=recipe_db.instructions,
        created_at=recipe_db.created_at,
        updated_at=recipe_db.updated_at,
    )


@router.post("/create", response_model=RecipeResponse)
def create_recipe(
    recipe_data: RecipeCreate,
    db: Session = Depends(get_db)
):
    """
    Create and save a new recipe
    
    Example request:
    ```json
    {
        "name": "Chocolate Chip Cookies",
        "ingredients": [
            {
                "name": "flour",
                "quantity": 2.0,
                "unit": "cup"
            }
        ],
        "servings": 24,
        "source": "manual",
        "notes": "My favorite recipe"
    }
    ```
    """
    try:
        # Generate unique ID
        recipe_id = str(uuid.uuid4())

        # Create database recipe
        recipe_db = RecipeDB(
            id=recipe_id,
            name=recipe_data.name,
            servings=recipe_data.servings,
            source=recipe_data.source,
            source_url=recipe_data.source_url,
            notes=recipe_data.notes,
            instructions=recipe_data.instructions,
        )

        # Add ingredients
        for idx, ingredient in enumerate(recipe_data.ingredients):
            ingredient_id = f"{recipe_id}_ing_{idx}"
            ing_db = IngredientDB(
                id=ingredient_id,
                recipe_id=recipe_id,
                name=ingredient.name,
                quantity=ingredient.quantity,
                unit=ingredient.unit,
                original_quantity=ingredient.original_quantity,
                original_unit=ingredient.original_unit,
                notes=ingredient.notes,
            )
            recipe_db.ingredients.append(ing_db)

        # Save to database
        db.add(recipe_db)
        db.commit()
        db.refresh(recipe_db)

        return RecipeResponse(
            recipe=_recipe_db_to_model(recipe_db),
            success=True,
            message="Recipe created successfully"
        )

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating recipe: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{recipe_id}", response_model=RecipeResponse)
def get_recipe(
    recipe_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve a recipe by ID
    """
    try:
        recipe_db = db.query(RecipeDB).filter(RecipeDB.id == recipe_id).first()

        if not recipe_db:
            raise HTTPException(status_code=404, detail="Recipe not found")

        return RecipeResponse(
            recipe=_recipe_db_to_model(recipe_db),
            success=True,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving recipe: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=RecipesListResponse)
def list_recipes(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    List all saved recipes with pagination
    
    Query parameters:
    - skip: Number of recipes to skip (default 0)
    - limit: Maximum recipes to return (default 50)
    """
    try:
        recipes_db = db.query(RecipeDB).offset(skip).limit(limit).all()
        total = db.query(RecipeDB).count()

        return RecipesListResponse(
            recipes=[_recipe_db_to_model(r) for r in recipes_db],
            total=total,
            success=True,
        )

    except Exception as e:
        logger.error(f"Error listing recipes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{recipe_id}", response_model=RecipeResponse)
def update_recipe(
    recipe_id: str,
    recipe_data: RecipeCreate,
    db: Session = Depends(get_db)
):
    """
    Update an existing recipe
    """
    try:
        recipe_db = db.query(RecipeDB).filter(RecipeDB.id == recipe_id).first()

        if not recipe_db:
            raise HTTPException(status_code=404, detail="Recipe not found")

        # Update fields
        recipe_db.name = recipe_data.name
        recipe_db.servings = recipe_data.servings
        recipe_db.source = recipe_data.source
        recipe_db.source_url = recipe_data.source_url
        recipe_db.notes = recipe_data.notes
        recipe_db.instructions = recipe_data.instructions
        recipe_db.updated_at = datetime.utcnow()

        # Update ingredients - delete old ones and add new
        db.query(IngredientDB).filter(IngredientDB.recipe_id == recipe_id).delete()

        for idx, ingredient in enumerate(recipe_data.ingredients):
            ingredient_id = f"{recipe_id}_ing_{idx}"
            ing_db = IngredientDB(
                id=ingredient_id,
                recipe_id=recipe_id,
                name=ingredient.name,
                quantity=ingredient.quantity,
                unit=ingredient.unit,
                original_quantity=ingredient.original_quantity,
                original_unit=ingredient.original_unit,
                notes=ingredient.notes,
            )
            recipe_db.ingredients.append(ing_db)

        db.commit()
        db.refresh(recipe_db)

        return RecipeResponse(
            recipe=_recipe_db_to_model(recipe_db),
            success=True,
            message="Recipe updated successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating recipe: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{recipe_id}")
def delete_recipe(
    recipe_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a recipe by ID
    """
    try:
        recipe_db = db.query(RecipeDB).filter(RecipeDB.id == recipe_id).first()

        if not recipe_db:
            raise HTTPException(status_code=404, detail="Recipe not found")

        db.delete(recipe_db)
        db.commit()

        return {
            'success': True,
            'message': f'Recipe {recipe_id} deleted successfully'
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting recipe: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{recipe_id}/scale")
def scale_recipe(
    recipe_id: str,
    target_servings: float,
    db: Session = Depends(get_db)
):
    """
    Scale a saved recipe to a different serving size
    
    Query parameter:
    - target_servings: Number of servings for scaled recipe
    
    Returns the recipe with all ingredients scaled accordingly
    """
    try:
        recipe_db = db.query(RecipeDB).filter(RecipeDB.id == recipe_id).first()

        if not recipe_db:
            raise HTTPException(status_code=404, detail="Recipe not found")

        if target_servings <= 0:
            raise ValueError("Target servings must be greater than 0")

        # Get ingredients as dicts
        ingredients_dict = [
            {
                'name': ing.name,
                'quantity': ing.quantity,
                'unit': ing.unit,
                'notes': ing.notes,
            }
            for ing in recipe_db.ingredients
        ]

        # Scale
        scaled_ingredients, scale_factor = ScalingService.scale_ingredients(
            ingredients_dict,
            recipe_db.servings,
            target_servings
        )

        # Convert back to Ingredient models
        scaled_ing_models = [
            Ingredient(**ing) for ing in scaled_ingredients
        ]

        # Create response recipe with scaled ingredients
        scaled_recipe = Recipe(
            id=recipe_db.id,
            name=recipe_db.name,
            ingredients=scaled_ing_models,
            servings=target_servings,
            source=recipe_db.source,
            source_url=recipe_db.source_url,
            notes=recipe_db.notes,
            instructions=recipe_db.instructions,
            created_at=recipe_db.created_at,
            updated_at=recipe_db.updated_at,
        )

        return {
            'recipe': scaled_recipe,
            'original_servings': recipe_db.servings,
            'target_servings': target_servings,
            'scale_factor': scale_factor,
            'success': True,
        }

    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error scaling recipe: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
