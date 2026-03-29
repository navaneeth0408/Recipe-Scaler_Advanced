# Recipe Scaler Backend - Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     CLIENT (Frontend)                            │
│        HTML/CSS/JavaScript + recipe-enhancements.js             │
│                                                                 │
│  Functions: scaleRecipe(), extractIngredients(), saveRecipe()  │
│  Communication: HTTP/CORS                                       │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                         HTTP/REST Requests
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│              FASTAPI APPLICATION (main.py)                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  CORS Middleware │ Error Handlers │ Logger │ Startup    │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                ┌────────────────┼────────────────┐
                │                │                │
                ▼                ▼                ▼
        ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
        │  ROUTES      │  │  SERVICES    │  │  DATABASE    │
        │              │  │              │  │              │
        │ ingredients  │  │ ingredient   │  │ SQLAlchemy   │
        │ scaling      │  │ scaling      │  │ ORM          │
        │ recipes      │  │ youtube      │  │ SQLite       │
        │ youtube      │  │              │  │              │
        └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
               │                 │                 │
               └─────────────────┼─────────────────┘
                                 │
                        ┌────────▼────────┐
                        │  MODELS/SCHEMAS │
                        │  (Pydantic)     │
                        │                 │
                        │ Ingredient      │
                        │ Recipe          │
                        │ YouTubeMetadata │
                        │ ScalingRequest  │
                        └─────────────────┘
```

## Request/Response Flow

### Example: Ingredient Extraction

```
Frontend                          Backend
   │                                │
   ├─────── POST /api/ingredients/extract ─────→
   │         {text: "2 cups flour"}              │
   │                                             │
   │                         ┌─ Validate Input   │
   │                         ├─ Parse Text      │
   │                         ├─ Extract Quantity │
   │                         ├─ Normalize Units │
   │                         └─ Return JSON     │
   │                                             │
   │         ← 200 OK {ingredients: [...]} ←───┤
   │                                             │
```

### Example: Recipe Scaling

```
Frontend                          Backend
   │                                │
   ├─ POST /api/scaling/scale ────→
   │  {ingredients, from_srv, to_srv}
   │                                │
   │                    ┌─ Validate Input
   │                    ├─ Calculate scale factor
   │                    ├─ Scale each ingredient
   │                    ├─ Suggest unit conversions
   │                    └─ Return scaled recipe
   │                                │
   │ ← 200 OK {scaled_ingredients} ←┤
   │                                │
```

## Route Layer

```
┌─────────────────────────────────────────┐
│            API ROUTES                   │
├─────────────────────────────────────────┤
│                                         │
│  /api/ingredients/                     │
│  ├─ POST extract      → Service logic  │
│  ├─ POST normalize    → Service logic  │
│  └─ POST detect-dups  → Service logic  │
│                                         │
│  /api/scaling/                         │
│  ├─ POST scale        → Service logic  │
│  ├─ POST convert-unit → Service logic  │
│  └─ GET suggest-unit  → Service logic  │
│                                         │
│  /api/recipes/                         │
│  ├─ POST create       → DB + Service   │
│  ├─ GET  list         → DB query       │
│  ├─ GET  /{id}        → DB query       │
│  ├─ PUT  /{id}        → DB update      │
│  ├─ DEL  /{id}        → DB delete      │
│  └─ POST /{id}/scale  → Service logic  │
│                                         │
│  /api/youtube/                         │
│  ├─ POST extract      → YouTube API    │
│  ├─ GET  metadata     → YouTube API    │
│  └─ GET  transcript   → YouTube API    │
│                                         │
└─────────────────────────────────────────┘
            │          │           │
            ▼          ▼           ▼
        ┌───────┬───────────┬─────────┐
        │Validate│Pass to   │DB/External
        │Input  │Services  │API Calls
        └───────┴───────────┴─────────┘
```

## Service Layer

```
┌────────────────────────────────────────────────────────────┐
│                    SERVICE LAYER                           │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────────────────────────────────────────┐         │
│  │  IngredientService                           │         │
│  ├──────────────────────────────────────────────┤         │
│  │ parse_quantity()         - Fraction parsing │         │
│  │ normalize_unit()         - Unit standard.   │         │
│  │ extract_modifiers()      - "Chopped", etc. │         │
│  │ extract_ingredients()    - Text parsing    │         │
│  │ detect_duplicates()      - Similarity       │         │
│  │ _similarity_ratio()      - String compare   │         │
│  └──────────────────────────────────────────────┘         │
│                                                            │
│  ┌──────────────────────────────────────────────┐         │
│  │  ScalingService                              │         │
│  ├──────────────────────────────────────────────┤         │
│  │ scale_ingredient()       - Scale 1 item     │         │
│  │ scale_ingredients()      - Scale multiple   │         │
│  │ convert_unit()           - Unit conversion  │         │
│  │ suggest_unit_conversion()- Better unit      │         │
│  │ _round_quantity()        - Round smartly    │         │
│  │ CONVERSIONS              - Unit tables      │         │
│  └──────────────────────────────────────────────┘         │
│                                                            │
│  ┌──────────────────────────────────────────────┐         │
│  │  YouTubeService                              │         │
│  ├──────────────────────────────────────────────┤         │
│  │ extract_video_id()       - Parse URL        │         │
│  │ get_youtube_metadata()   - Fetch info       │         │
│  │ get_youtube_transcript() - Get captions     │         │
│  │ extract_ingredients_from_transcript() - Parse
│  │ is_valid_youtube_url()   - Validate        │         │
│  └──────────────────────────────────────────────┘         │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

## Database Layer

```
┌──────────────────────────────────────────┐
│         DATABASE (SQLite)                │
├──────────────────────────────────────────┤
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  recipes                           │ │
│  ├────────────────────────────────────┤ │
│  │ id (PK)                            │ │
│  │ name                               │ │
│  │ servings                           │ │
│  │ source (youtube/manual)            │ │
│  │ source_url                         │ │
│  │ notes                              │ │
│  │ instructions (JSON)                │ │
│  │ created_at                         │ │
│  │ updated_at                         │ │
│  └────────┬──────────────────────────┘ │
│           │ 1──→M relationship         │
│  ┌────────▼──────────────────────────┐ │
│  │  ingredients                       │ │
│  ├────────────────────────────────────┤ │
│  │ id (PK)                            │ │
│  │ recipe_id (FK)                     │ │
│  │ name                               │ │
│  │ quantity                           │ │
│  │ unit                               │ │
│  │ original_quantity                  │ │
│  │ original_unit                      │ │
│  │ notes                              │ │
│  │ created_at                         │ │
│  └────────────────────────────────────┘ │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  youtube_cache                     │ │
│  ├────────────────────────────────────┤ │
│  │ id (PK)                            │ │
│  │ video_id (UNIQUE)                  │ │
│  │ title                              │ │
│  │ description                        │ │
│  │ channel_name                       │ │
│  │ thumbnail_url                      │ │
│  │ duration                           │ │
│  │ view_count                         │ │
│  │ upload_date                        │ │
│  │ metadata (JSON)                    │ │
│  │ created_at / updated_at            │ │
│  └────────────────────────────────────┘ │
│                                          │
└──────────────────────────────────────────┘
```

## Data Model Relationships

```
Recipe
  ├─ name: string
  ├─ servings: float
  ├─ source: string (youtube|manual)
  ├─ created_at: timestamp
  └─ ingredients: [Ingredient]  ← Has many
                    │
                    ├─ name: string
                    ├─ quantity: float
                    ├─ unit: string
                    ├─ original_quantity: float
                    ├─ original_unit: string
                    └─ notes: string
```

## API Endpoint Groups

### Ingredient Operations
```
/api/ingredients/
├─ extract         POST    Extract from text
├─ normalize       POST    Standardize units
└─ detect-dups     POST    Find duplicates
```

### Scaling Operations
```
/api/scaling/
├─ scale           POST    Scale recipe
├─ convert-unit    POST    Convert units
└─ suggest-unit    GET     Better unit
```

### Recipe Management
```
/api/recipes/
├─ create          POST    New recipe
├─ list            GET     All recipes
├─ get             GET     One recipe
├─ update          PUT     Modify recipe
├─ delete          DELETE  Remove recipe
└─ scale           POST    Scale specific recipe
```

### YouTube Integration
```
/api/youtube/
├─ extract         POST    Metadata + ingredients
├─ metadata        GET     Video info only
└─ transcript      GET     Video captions
```

### Health & Info
```
/
├─ GET /           Info page
├─ GET /api/health Health check
├─ GET /api/docs   Swagger UI
└─ GET /api/redoc  ReDoc documentation
```

## Deployment Topology

### Development
```
┌─────────────────────────────────┐
│     Frontend (localhost:3000)    │
└──────────────┬──────────────────┘
               │ HTTP/CORS
               ▼
┌─────────────────────────────────┐
│   Backend (localhost:8000)       │
│   ├─ FastAPI + Uvicorn          │
│   ├─ SQLite Database            │
│   └─ In-memory processing       │
└─────────────────────────────────┘
```

### Production (Docker)
```
┌──────────────────────────────────────────┐
│  Docker Container                        │
│  ┌──────────────────────────────────┐   │
│  │ Python 3.11 Environment          │   │
│  │ ┌────────────────────────────┐   │   │
│  │ │ Uvicorn Server (port 8000) │   │   │
│  │ │ ┌──────────────────────┐   │   │   │
│  │ │ │ FastAPI Application  │   │   │   │
│  │ │ │ ├─ Routes           │   │   │   │
│  │ │ │ ├─ Services         │   │   │   │
│  │ │ │ └─ Database (SQLite)│   │   │   │
│  │ │ └──────────────────────┘   │   │   │
│  │ └────────────────────────────┘   │   │
│  └──────────────────────────────────┘   │
└──────────────────────────────────────────┘
            │
            │ Port 8000 (exposed)
            ▼
┌──────────────────────────────────────────┐
│  Optional: Nginx Reverse Proxy           │
│  ├─ Load balancing                       │
│  ├─ SSL/TLS termination                  │
│  └─ Compression                          │
└──────────────────────────────────────────┘
```

## Processing Pipeline Example

### Ingredient Extraction Pipeline
```
Raw Text Input
    │
    ▼
┌─────────────────────────────┐
│ Parse Quantity              │
│ "2 cups flour, 1/2 cup..."  │
├─────────────────────────────┤
│ quantity = 2.0              │
│ unit = "cups"               │
│ remainder = "flour, 1/2..." │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│ Normalize Units             │
│ "cups" → "cup"              │
│ "tblsp" → "tablespoon"      │
├─────────────────────────────┤
│ normalized_unit = "cup"     │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│ Extract Modifiers           │
│ "flour, chopped, fresh"     │
├─────────────────────────────┤
│ name = "flour"              │
│ notes = "chopped, fresh"    │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│ Detect Duplicates           │
│ Compare all ingredients      │
├─────────────────────────────┤
│ duplicates = []             │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│ Return Structured Data      │
│ [Ingredient, Ingredient]    │
└─────────────────────────────┘
```

## External API Integration

```
┌─────────────────────────────────────┐
│     Recipe Scaler Backend           │
│  ┌───────────────────────────────┐  │
│  │ YouTube Service              │  │
│  │  extract_video_id()          │  │
│  │  get_youtube_metadata()      │  │
│  │  get_youtube_transcript()    │  │
│  └───┬──────────────────────────┘  │
│      │                              │
│      ├─ youtube-transcript-api      │
│      │  (Get captions/transcripts)  │
│      │                              │
│      └─ yt-dlp                      │
│         (Get video metadata)        │
│                                     │
└─────────────────────────────────────┘
         │           │
         ▼           ▼
    YouTube API  YouTube HTML
```

## Error Handling Flow

```
Request arrives
    │
    ▼
Route Handler
    │
    ├─ Input Validation (Pydantic)
    │  │
    │  └─ Error? → HTTPException 400 → Client
    │
    ├─ Business Logic (Services)
    │  │
    │  └─ Error? → HTTPException 500 → Client
    │
    ├─ Database Operations
    │  │
    │  └─ Error? → Rollback → HTTPException 500 → Client
    │
    └─ Success → JSON Response 200 → Client
```

## Summary

The architecture follows a **layered pattern**:

1. **Route Layer**: HTTP endpoint handlers
2. **Service Layer**: Business logic (extraction, scaling, YouTube)
3. **Database Layer**: Data persistence (SQLAlchemy + SQLite)
4. **Model Layer**: Data validation (Pydantic schemas)
5. **External APIs**: YouTube integration

This design ensures:
- ✅ Separation of concerns
- ✅ Testability
- ✅ Reusability
- ✅ Maintainability
- ✅ Scalability

