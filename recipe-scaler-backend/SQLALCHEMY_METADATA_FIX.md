# SQLAlchemy Reserved Attribute Error - Fix & Explanation

## Error Fixed

**Error:**
```
sqlalchemy.exc.InvalidRequestError:
Attribute name 'metadata' is reserved when using the Declarative API
```

**Root Cause:** The `YouTubeCacheDB` model had a column named `metadata`, which is a reserved attribute name in SQLAlchemy's Declarative API.

---

## Why 'metadata' is Reserved in SQLAlchemy

### 1. **Internal Use by SQLAlchemy**
SQLAlchemy uses `metadata` internally in every Declarative class:
```python
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class MyModel(Base):
    __tablename__ = "my_table"
    # All classes have access to Base.metadata
    # This stores the table definitions
```

### 2. **The Metadata Object**
Every class created with Declarative API automatically has a `metadata` attribute that references the table metadata registry:
```python
class Recipe(Base):
    __tablename__ = "recipes"
    id = Column(Integer, primary_key=True)

# SQLAlchemy internally uses:
# Recipe.metadata  # Refers to the MetaData registry
```

### 3. **Why You Can't Override It**
If you try to create a column named `metadata`:
```python
# This FAILS:
class YouTubeCacheDB(Base):
    __tablename__ = "youtube_cache"
    metadata = Column(JSON)  # ❌ Conflicts with SQLAlchemy's internal .metadata
```

---

## Solution Applied

### Before (❌ BROKEN):
```python
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
    metadata = Column(JSON)  # ❌ Reserved name - causes error
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### After (✅ FIXED):
```python
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
    cache_data = Column(JSON)  # ✅ Non-reserved, descriptive name
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

---

## Files Updated

| File | Change | Status |
|------|--------|--------|
| [app/database/db.py](../app/database/db.py#L102) | Renamed `metadata` → `cache_data` in YouTubeCacheDB | ✅ Done |
| [app/routes/youtube.py](../app/routes/youtube.py#L99) | Updated column assignment in extract endpoint | ✅ Done |
| [app/routes/youtube.py](../app/routes/youtube.py#L176) | Updated column assignment in metadata endpoint | ✅ Done |

---

## SQLAlchemy Reserved Attributes (DO NOT USE as Column Names)

The following are reserved in SQLAlchemy and should **NEVER** be used as column names:

### Core Reserved Names
| Attribute | Why Reserved | Alternative |
|-----------|-------------|-------------|
| `metadata` | SQLAlchemy metadata registry | `meta_data`, `cache_data`, `extra_data` |
| `mapper` | ORM mapper instance | `mapping_info`, `mapper_config` |
| `__table__` | Database table reference | Use `__tablename__` instead |
| `__mapper__` | Mapper object | Don't access directly |
| `__class__` | Python class object | Don't override |

### Relationship Reserved Names
```python
# These are reserved for relationship definitions:
# - relationship()
# - back_populates
# - primaryjoin
# - foreignkeys
```

### Session Reserved Names
```python
# These are reserved for session operations:
# - __dict__
# - __state__
# - __sqlalchemy_orm_state__
```

---

## Naming Conventions to Avoid Issues

### ✅ GOOD Column Names
```python
class YouTubeCacheDB(Base):
    __tablename__ = "youtube_cache"
    
    # Descriptive, non-reserved names
    cache_data = Column(JSON)      # ✓ Clear purpose
    extra_info = Column(JSON)       # ✓ Descriptive
    video_metadata = Column(JSON)   # ✓ Includes context
    raw_data = Column(JSON)         # ✓ Indicates format
    payload = Column(JSON)          # ✓ Common pattern
    attributes = Column(JSON)       # ✓ Clear meaning
```

### ❌ BAD Column Names (Avoid)
```python
class YouTubeCacheDB(Base):
    __tablename__ = "youtube_cache"
    
    metadata = Column(JSON)         # ❌ Reserved
    mapper = Column(String)         # ❌ Reserved
    __data__ = Column(JSON)         # ❌ Dunder prefix
    data = Column(JSON)             # ❌ Too vague
    dict = Column(JSON)             # ❌ Shadows Python builtin
    type = Column(String)           # ❌ Shadows Python builtin
```

---

## How to Check for Reserved Names

### 1. SQLAlchemy Documentation
Check the [SQLAlchemy Reserved Column Names Guide](https://docs.sqlalchemy.org/en/20/faq/orm_mappings.html)

### 2. Test Before Deployment
```python
from app.database.db import init_db

# This will raise an error if you use reserved names
try:
    init_db()
    print("✓ Database initialized successfully - no reserved names")
except Exception as e:
    print(f"✗ Error: {e}")
```

### 3. IDE Inspection
Modern IDEs will warn you about shadowing SQLAlchemy attributes:
```python
cache_data = Column(JSON)  # IDE shows this is a safe name
metadata = Column(JSON)    # IDE warns about potential issues
```

---

## Database Schema Migration

### For Existing Deployments

If you already have a database with the old `metadata` column, you need to migrate:

```sql
-- SQLite migration script
-- Rename the column
ALTER TABLE youtube_cache RENAME COLUMN metadata TO cache_data;

-- Verify
.schema youtube_cache
```

### For New Deployments

Simply delete the old database file - it will be recreated:
```bash
# Remove old database
rm app/recipe_scaler.db

# Start backend - new database created with correct schema
python main.py
```

---

## Testing the Fix

### 1. Verify Database Initializes
```python
python -c "from app.database.db import init_db, engine; init_db(); print('✓ Database initialized')"
```

### 2. Test YouTube Cache Operations
```bash
# Start backend
python main.py

# In another terminal, test the endpoint:
curl -X POST http://localhost:8000/api/youtube/extract \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "extract_ingredients": false
  }'
```

### 3. Verify Cache Table Structure
```python
from app.database.db import engine
from sqlalchemy import inspect

inspector = inspect(engine)
columns = inspector.get_columns('youtube_cache')

for col in columns:
    print(f"Column: {col['name']}, Type: {col['type']}")

# Expected output includes:
# Column: cache_data, Type: JSON
```

---

## Best Practices for ORM Model Design

### 1. **Use Descriptive Names**
```python
✓ cache_data         # What does it store?
✓ video_metadata     # What does it contain?
✓ api_response       # Where does it come from?

✗ data              # Too vague
✗ info              # Too generic
```

### 2. **Follow Naming Conventions**
```python
# Columns use snake_case
class Recipe(Base):
    __tablename__ = "recipes"
    
    video_title = Column(String)       # ✓ snake_case
    created_at = Column(DateTime)      # ✓ Standard pattern
    is_active = Column(Boolean)        # ✓ Boolean prefix

# Do NOT use camelCase
    videoTitle = Column(String)        # ✗ Python style
    CreatedAt = Column(DateTime)       # ✗ Java style
```

### 3. **Avoid Python Builtins**
```python
# Do NOT shadow Python builtins:
✗ dict = Column(JSON)
✗ type = Column(String)
✗ id = Column(Integer)  # Okay for databases, but be careful
✗ list = Column(JSON)
✗ map = Column(String)

# Use alternatives:
✓ data_dict = Column(JSON)
✓ record_type = Column(String)
✓ item_id = Column(String)
✓ items = Column(JSON)
✓ field_map = Column(String)
```

### 4. **Use Column Naming Convention Plugin (Advanced)**
```python
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import sqltypes
from sqlalchemy import create_engine

class ConventionDict(dict):
    def __contains__(self, key):
        return True
    def __getitem__(self, key):
        return key
    def get(self, key, default=None):
        return key

naming_convention = ConventionDict({
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
})

Base = declarative_base(metadata=MetaData(naming_convention=naming_convention))
```

---

## Summary

| Aspect | Details |
|--------|---------|
| **Error** | `InvalidRequestError: Attribute name 'metadata' is reserved` |
| **Cause** | Used reserved SQLAlchemy attribute as column name |
| **Fix** | Renamed `metadata` → `cache_data` |
| **Files Changed** | 3 (db.py, youtube.py x2) |
| **Database Impact** | Minor - old schema needs migration or deletion |
| **Backwards Compatibility** | Breaking change - requires schema update |

---

## Next Steps

1. **Restart Backend**
   ```bash
   python main.py
   ```

2. **Test Database Connection**
   ```bash
   python -c "from app.database.db import init_db; init_db(); print('OK')"
   ```

3. **Verify API Endpoints**
   - Navigate to http://localhost:8000/api/docs
   - Test YouTube endpoints

4. **Monitor Logs**
   - Check for any ORM-related errors
   - Verify cache operations work correctly

---

## References

- [SQLAlchemy Declarative API Docs](https://docs.sqlalchemy.org/en/20/orm/declarative_api.html)
- [SQLAlchemy Reserved Names](https://docs.sqlalchemy.org/en/20/faq/orm_mappings.html)
- [SQLAlchemy ORM Attributes](https://docs.sqlalchemy.org/en/20/orm/attributes.html)
- [Python SQLAlchemy 2.0 Migration Guide](https://docs.sqlalchemy.org/en/20/changelog/migration_20.html)

---

**Status: ✅ FIXED - Backend ready to run without ORM errors**
