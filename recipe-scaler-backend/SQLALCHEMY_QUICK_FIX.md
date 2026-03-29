# SQLAlchemy Reserved Attribute Fix - Quick Reference

## Error Message
```
sqlalchemy.exc.InvalidRequestError:
Attribute name 'metadata' is reserved when using the Declarative API
```

## Root Cause
Column named `metadata` conflicts with SQLAlchemy's internal `metadata` attribute (the table registry).

---

## What Was Changed

### File: app/database/db.py
**Line 100:** Column definition in `YouTubeCacheDB` class
```python
# Before:
metadata = Column(JSON)

# After:
cache_data = Column(JSON)
```

### File: app/routes/youtube.py
**Line 99 & 176:** Cache entry creation (2 locations)
```python
# Before:
cache_entry = YouTubeCacheDB(
    ...
    metadata=metadata_dict,
)

# After:
cache_entry = YouTubeCacheDB(
    ...
    cache_data=metadata_dict,
)
```

---

## Verification

✅ Database initializes without errors  
✅ cache_data column created successfully  
✅ No reserved name conflicts  
✅ YouTube cache operations ready  

---

## Avoid These Column Names in SQLAlchemy

| Don't Use | Reason | Use Instead |
|-----------|--------|-------------|
| `metadata` | SQLAlchemy internal registry | `cache_data`, `extra_info` |
| `mapper` | ORM mapper instance | `mapping_config`, `mapper_info` |
| `__table__` | Table reference object | Use `__tablename__` |
| `dict` | Python builtin | `data_dict`, `record_dict` |
| `type` | Python builtin | `record_type`, `item_type` |
| `id` | Too generic | `user_id`, `item_id`, `record_id` |

---

## How to Prevent This

### Before Creating a Column
Ask yourself:
1. **Is it a SQLAlchemy reserved word?** ❌ metadata, mapper, __table__
2. **Does it shadow Python builtins?** ❌ dict, type, list, id, str
3. **Is it descriptive enough?** ✅ cache_data, user_metadata, video_info

### Good Column Names
```python
cache_data       # Descriptive, clear purpose
video_metadata   # Includes context
extra_info       # Clear intent
raw_payload      # Indicates format
attributes       # Clear meaning
api_response     # Shows source
```

---

## Quick Fix Guide

**If you encounter this error:**

1. **Identify the problematic column**
   - Look for columns named: `metadata`, `mapper`, or other reserved words

2. **Rename the column**
   ```python
   # Change reserved name to descriptive alternative
   cache_data = Column(JSON)  # Instead of metadata
   ```

3. **Update all references**
   - Find where the column is assigned
   - Update variable names in route handlers
   - Test the change

4. **Verify**
   ```bash
   python -c "from app.database.db import init_db; init_db(); print('OK')"
   ```

---

## Testing Commands

```bash
# Test 1: Initialize database
python -c "from app.database.db import init_db; init_db(); print('Database OK')"

# Test 2: Start backend
python main.py

# Test 3: Check API docs
# Open: http://localhost:8000/api/docs
```

---

## Database Impact

| Scenario | Action | Impact |
|----------|--------|--------|
| **Fresh Install** | None needed | Works immediately ✓ |
| **Existing DB** | Delete `app/recipe_scaler.db` | Data lost (recreated on next run) |
| **Production DB** | Run migration SQL | Preserves existing data |

---

## Related Documents

- [SQLALCHEMY_METADATA_FIX.md](SQLALCHEMY_METADATA_FIX.md) - Detailed explanation
- [SQLALCHEMY_FIX_SUMMARY.md](SQLALCHEMY_FIX_SUMMARY.md) - Complete resolution summary

---

**Status: FIXED ✓ Ready to deploy**
