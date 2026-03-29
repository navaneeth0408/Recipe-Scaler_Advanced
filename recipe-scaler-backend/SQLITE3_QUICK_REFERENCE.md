# SQLite3 Quick Reference - Recipe Scaler Backend

## ✓ Problem Fixed

| Issue | Solution | Status |
|-------|----------|--------|
| `pip install sqlite3` fails | sqlite3 is in Python stdlib | ✓ Fixed |
| sqlite3 in requirements.txt | Removed from file | ✓ Fixed |
| Unclear why error occurs | Documented in SQLITE3_EXPLANATION.md | ✓ Explained |
| Need working example | Provided in SQLITE3_EXAMPLE.py | ✓ Added |

---

## Updated requirements.txt Status

**Before (❌ BROKEN):**
```txt
fastapi==0.104.1
sqlalchemy==2.0.23
sqlite3          ← WRONG: Cannot pip install
```

**After (✅ WORKING):**
```txt
fastapi==0.104.1
sqlalchemy==2.0.23
# sqlite3 removed - available in Python stdlib
```

---

## Your Current Implementation (Already Correct)

### Location: [app/database/db.py](../app/database/db.py)

```python
from sqlalchemy import create_engine

# ✓ Correct: Uses SQLite with SQLAlchemy
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'recipe_scaler.db')}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
```

**Why this works:**
- SQLAlchemy automatically uses the `sqlite3` standard library module
- No additional pip installation needed
- Handles all database operations

---

## Installation & Verification

### 1. Install (Correct Method)
```bash
cd c:\Users\DELL\OneDrive\Desktop\recipe-scaler-backend
pip install -r requirements.txt
```

### 2. Verify sqlite3 is Available
```bash
python -c "import sqlite3; print(f'SQLite available: {sqlite3.version}')"
```

Expected output:
```
SQLite available: 2.6.0
```

### 3. Run Backend
```bash
python main.py
```

---

## Code Patterns (Your Project)

### Using SQLAlchemy (Recommended - Your Approach)
```python
# Models access SQLite through SQLAlchemy
from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine("sqlite:///./recipe_scaler.db")
Base = declarative_base()

class Recipe(Base):
    __tablename__ = "recipes"
    id = Column(String, primary_key=True)
    name = Column(String)

# ✓ SQLAlchemy handles sqlite3 internally - no import needed
```

### Direct sqlite3 Usage (If Needed)
```python
# Raw SQLite access (optional - use only if needed)
import sqlite3

conn = sqlite3.connect('recipe_scaler.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM recipes")
results = cursor.fetchall()
conn.close()

# ✓ Standard library - no pip installation
```

---

## Common Issues & Fixes

### Issue 1: "ModuleNotFoundError: No module named 'sqlite3'"
**Solution:** Update Python to 3.2+ (all modern Python versions include sqlite3)

### Issue 2: "Database is locked" in SQLite
**Solution:** Already in your code!
```python
# ✓ Correct: Handles SQLite threading
create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
```

### Issue 3: Database file permissions
**Solution:** Ensure write access to `app/` directory
```bash
# Verify directory is writable
ls -la app/
chmod 755 app/  # If needed
```

---

## Files Modified

| File | Change | Status |
|------|--------|--------|
| [requirements.txt](../requirements.txt) | Removed `sqlite3` line | ✓ Done |
| New: SQLITE3_EXPLANATION.md | Detailed explanation | ✓ Created |
| New: SQLITE3_EXAMPLE.py | Working example code | ✓ Created |
| [app/database/db.py](../app/database/db.py) | No changes needed | ✓ Already correct |

---

## Next Steps

1. **Verify Installation Works**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Application**
   ```bash
   python main.py
   ```

3. **Test Database**
   ```bash
   python -c "from app.database.db import engine; print('✓ Database connected')"
   ```

4. **Review Your Code**
   - Your SQLAlchemy implementation is correct
   - sqlite3 standard library is automatically used
   - No additional configuration needed

---

## Industry Standard Notes

✅ **This approach is:**
- Used by Django, Flask, FastAPI professionals
- Recommended by Python documentation
- Final-year project appropriate
- Production-ready
- Zero external dependencies for SQLite

❌ **Never do:**
- Try to `pip install sqlite3`
- List sqlite3 in requirements.txt
- Worry about SQLite version conflicts
- Need to manually configure SQLite

---

## Documentation References

- [Python sqlite3 Documentation](https://docs.python.org/3/library/sqlite3.html)
- [SQLAlchemy SQLite Engine](https://docs.sqlalchemy.org/en/20/dialects/sqlite.html)
- [FastAPI Database Guide](https://fastapi.tiangolo.com/advanced/sql-databases/)

---

**Status: ✓ RESOLVED - Backend ready to run without dependency errors**
