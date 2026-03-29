"""
FastAPI application entry point
Main application setup with route registration and CORS configuration
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app.database.db import init_db
from app.routes import ingredients, scaling, recipes, youtube, youtube_search
from app.routes import ingredient_substitutions

# Try to import AI routes (optional - requires heavy ML dependencies)
try:
    from app.routes import ai
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    import logging
    logging.warning("AI routes not available - missing ML dependencies (transformers, torch, spacy)")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Recipe Scaler API",
    description="REST API for recipe scaling, ingredient extraction, and management",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

# ============================================================================
# CORS CONFIGURATION
# ============================================================================
# Allow requests from frontend (adjust origins for your deployment)
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5000",
    "http://localhost:5500",     # Frontend dev server
    "http://localhost:5501",     # Alternate dev port
    "http://localhost:8080",     # Frontend HTTP server
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5000",
    "http://127.0.0.1:5500",
    "http://127.0.0.1:5501",     # Alternate dev port
    "http://127.0.0.1:8080",
    "file://",  # For Electron/desktop apps
]

# In production, be more restrictive with origins
if os.getenv("ENVIRONMENT") == "production":
    ALLOWED_ORIGINS = [
        os.getenv("FRONTEND_URL", "https://yourdomain.com"),
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized successfully")


# ============================================================================
# ROUTE REGISTRATION
# ============================================================================
# Include route modules
app.include_router(ingredients.router)
app.include_router(scaling.router)
app.include_router(recipes.router)
app.include_router(youtube.router)
app.include_router(youtube_search.router)
app.include_router(ingredient_substitutions.router)

# Include AI routes only if dependencies are available
if AI_AVAILABLE:
    app.include_router(ai.router)

# ============================================================================
# ROOT ENDPOINT
# ============================================================================
@app.get("/", tags=["root"])
async def root():
    """Root endpoint - API information"""
    return {
        "name": "Recipe Scaler API",
        "version": "1.0.0",
        "description": "REST API for recipe scaling and ingredient management",
        "endpoints": {
            "docs": "/api/docs",
            "openapi": "/api/openapi.json",
        },
        "base_url": "/api",
    }


@app.get("/api/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Recipe Scaler API is running",
    }


# ============================================================================
# ERROR HANDLERS
# ============================================================================
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle ValueError exceptions"""
    return JSONResponse(
        status_code=400,
        content={
            "error": str(exc),
            "success": False,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "details": str(exc) if os.getenv("DEBUG") == "true" else None,
            "success": False,
        },
    )


# ============================================================================
# RUNNING THE APP
# ============================================================================
if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    debug = os.getenv("DEBUG", "false").lower() == "true"

    logger.info(f"Starting Recipe Scaler API on {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )
