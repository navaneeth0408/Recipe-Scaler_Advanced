"""
Database configuration and SQLAlchemy models
Handles SQLite database setup and ORM models
"""

import os
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Float, DateTime, Text, Integer, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from typing import Generator

# Database URL - SQLite
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'recipe_scaler.db')}"

# SQLAlchemy setup
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ============================================================================
# DATABASE MODELS
# ============================================================================

class RecipeDB(Base):
    """Database model for recipes"""
    __tablename__ = "recipes"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    servings = Column(Float)
    source = Column(String)  # "youtube" or "manual"
    source_url = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    instructions = Column(JSON, nullable=True)  # List of instruction strings
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    view_count = Column(Integer, default=0)

    # Relationships
    ingredients = relationship("IngredientDB", back_populates="recipe", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "servings": self.servings,
            "source": self.source,
            "source_url": self.source_url,
            "notes": self.notes,
            "instructions": self.instructions,
            "ingredients": [ing.to_dict() for ing in self.ingredients],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "view_count": self.view_count,
        }


class IngredientDB(Base):
    """Database model for ingredients"""
    __tablename__ = "ingredients"

    id = Column(String, primary_key=True, index=True)
    recipe_id = Column(String, ForeignKey("recipes.id"), index=True)
    name = Column(String, index=True)
    quantity = Column(Float)
    unit = Column(String)
    original_quantity = Column(Float, nullable=True)
    original_unit = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    recipe = relationship("RecipeDB", back_populates="ingredients")

    def to_dict(self):
        return {
            "name": self.name,
            "quantity": self.quantity,
            "unit": self.unit,
            "original_quantity": self.original_quantity,
            "original_unit": self.original_unit,
            "notes": self.notes,
        }


class YouTubeCacheDB(Base):
    """Cache for YouTube metadata to reduce API calls"""
    __tablename__ = "youtube_cache"

    id = Column(String, primary_key=True, index=True)
    video_id = Column(String, unique=True, index=True)
    title = Column(String)
    description = Column(Text)
    channel_name = Column(String)
    thumbnail_url = Column(String)
    duration = Column(String, nullable=True)
    view_count = Column(Integer, nullable=True)
    upload_date = Column(String, nullable=True)
    cache_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "video_id": self.video_id,
            "title": self.title,
            "description": self.description,
            "channel_name": self.channel_name,
            "thumbnail_url": self.thumbnail_url,
            "duration": self.duration,
            "view_count": self.view_count,
            "upload_date": self.upload_date,
        }


class YouTubeTranscriptDB(Base):
    """Cache for YouTube audio transcripts"""
    __tablename__ = "youtube_transcripts"

    id = Column(String, primary_key=True, index=True)
    video_id = Column(String, unique=True, index=True)
    title = Column(String)
    transcript = Column(Text)  # Full transcribed text
    transcript_segments = Column(JSON, nullable=True)  # List of segment dicts with timestamps
    duration = Column(Float, nullable=True)  # Video duration in seconds
    language = Column(String, default="en")
    extraction_method = Column(String)  # "audio", "youtube_api", "manual"
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "video_id": self.video_id,
            "title": self.title,
            "transcript": self.transcript,
            "transcript_segments": self.transcript_segments,
            "duration": self.duration,
            "language": self.language,
            "extraction_method": self.extraction_method,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def init_db():
    """Initialize database - create all tables"""
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator:
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
