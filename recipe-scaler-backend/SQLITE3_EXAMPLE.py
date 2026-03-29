"""
Minimal SQLite3 + FastAPI Working Example

This module demonstrates the correct way to use SQLite3 with FastAPI.
Copy this to understand the implementation pattern.
"""

from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

# ============================================================================
# DATABASE SETUP (This is what you have - CORRECT approach)
# ============================================================================

# Database URL - SQLite (no pip installation needed, uses stdlib sqlite3)
DATABASE_URL = "sqlite:///./recipe_scaler.db"

# Create engine with SQLite-specific settings
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Required for SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ============================================================================
# DATABASE MODELS (ORM Layer)
# ============================================================================

class RecipeModel(Base):
    """SQLAlchemy ORM model for recipes table"""
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    servings = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================================================
# PYDANTIC SCHEMAS (API Request/Response)
# ============================================================================

class RecipeBase(BaseModel):
    """Base schema for recipe data"""
    name: str
    servings: int


class RecipeCreate(RecipeBase):
    """Schema for creating a recipe"""
    pass


class RecipeResponse(RecipeBase):
    """Schema for recipe response"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True  # SQLAlchemy compatibility


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="Recipe Scaler - SQLite Example",
    description="Demonstrates correct SQLite3 usage with FastAPI",
    version="1.0.0"
)


# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def init_db():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)


@app.on_event("startup")
async def startup():
    """Initialize database on app startup"""
    init_db()
    print("✓ Database initialized successfully")
    print("✓ SQLite3 module: Available from Python standard library")


# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================

def get_db() -> Session:
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "SQLite",
        "message": "No extra sqlite3 installation needed - uses Python stdlib"
    }


@app.post("/recipes", response_model=RecipeResponse)
async def create_recipe(recipe: RecipeCreate, db: Session = Depends(get_db)):
    """
    Create a new recipe in SQLite database
    
    Requirements satisfied:
    ✓ Uses standard library sqlite3 (via SQLAlchemy)
    ✓ No pip installation needed
    ✓ Professional FastAPI implementation
    ✓ Final-year project appropriate
    """
    db_recipe = RecipeModel(name=recipe.name, servings=recipe.servings)
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    return db_recipe


@app.get("/recipes/{recipe_id}", response_model=RecipeResponse)
async def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """Retrieve a recipe from SQLite database"""
    recipe = db.query(RecipeModel).filter(RecipeModel.id == recipe_id).first()
    if not recipe:
        return {"error": "Recipe not found"}
    return recipe


@app.get("/recipes", response_model=List[RecipeResponse])
async def list_recipes(db: Session = Depends(get_db)):
    """List all recipes from SQLite database"""
    recipes = db.query(RecipeModel).all()
    return recipes


# ============================================================================
# DIRECT SQLITE3 USAGE (If needed without ORM)
# ============================================================================

@app.get("/info/sqlite")
async def sqlite_info():
    """
    Direct sqlite3 module access (optional)
    Shows that sqlite3 is available from standard library
    """
    import sqlite3
    
    return {
        "sqlite3_version": sqlite3.version,
        "sqlite_library_version": sqlite3.sqlite_version,
        "note": "sqlite3 is part of Python standard library - no pip install needed"
    }


# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


# ============================================================================
# HOW TO USE THIS EXAMPLE
# ============================================================================
"""
1. INSTALL DEPENDENCIES (sqlite3 NOT included):
   $ pip install -r requirements.txt
   
   requirements.txt should contain:
   - fastapi
   - sqlalchemy
   - uvicorn
   (NO sqlite3 - it's in the standard library!)

2. RUN THE APPLICATION:
   $ python main.py
   
   Or with uvicorn directly:
   $ uvicorn main:app --reload

3. TEST ENDPOINTS:
   
   Health check:
   GET http://localhost:8000/health
   
   Create recipe:
   POST http://localhost:8000/recipes
   {
       "name": "Pasta Carbonara",
       "servings": 4
   }
   
   Get recipe:
   GET http://localhost:8000/recipes/1
   
   List all recipes:
   GET http://localhost:8000/recipes
   
   SQLite info:
   GET http://localhost:8000/info/sqlite

4. DATABASE FILE:
   - Created automatically as: recipe_scaler.db
   - SQLite database (single file, easy to backup)
   - No server process needed

5. VIEW DOCS:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc
"""
