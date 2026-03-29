# SQLite3 & pip - Comprehensive Explanation

## Problem Summary

**Error:**
```
ERROR: Could not find a version that satisfies the requirement sqlite3
ERROR: No matching distribution found for sqlite3
```

**Root Cause:** `sqlite3` is included in the Python standard library and **cannot** be installed via pip.

---

## Why sqlite3 Should NOT Be Installed via pip

### 1. **Part of Python Standard Library**
   - `sqlite3` is built into Python 3.x since Python 3.2
   - It's included with every Python installation
   - No external installation is required

### 2. **PyPI Distribution Does Not Exist**
   - There is no official `sqlite3` package on PyPI (Python Package Index)
   - pip cannot find a package to install
   - This is by design to avoid confusion with the standard library module

### 3. **Version Management**
   - `sqlite3` version matches your Python version
   - It's automatically updated when Python is updated
   - No dependency conflicts occur

### 4. **Security & Stability**
   - Official Python releases maintain `sqlite3` security patches
   - Using the standard library version ensures compatibility
   - You get official support from the Python core team

### 5. **Best Practices**
   - Professional Python projects never list `sqlite3` in requirements.txt
   - It's an anti-pattern to attempt pip installation
   - Final-year projects must follow industry standards

---

## Correct Implementation

### Step 1: Remove from requirements.txt ✓
```text
# WRONG - Do not include this
sqlite3

# CORRECT - Remove entirely and use the standard library
```

### Step 2: Import and Use in Code

**Standard Library Approach (Direct SQL):**
```python
import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()
cursor.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)')
conn.commit()
conn.close()
```

**SQLAlchemy Approach (Your Project):**
```python
from sqlalchemy import create_engine

# SQLite URL for SQLAlchemy
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
```

---

## Your Current Setup (Correct)

Your project is already correctly configured:

✅ **[db.py](../app/database/db.py)** uses SQLAlchemy with SQLite:
```python
from sqlalchemy import create_engine

DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'recipe_scaler.db')}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
```

✅ **Requirements.txt** has been updated to remove the problematic `sqlite3` line

✅ **No additional dependencies needed** - SQLAlchemy handles all SQLite operations

---

## Installation & Setup

### 1. Install Dependencies (Correct Way)
```bash
pip install -r requirements.txt
```

### 2. Initialize Database
```bash
python main.py
```

### 3. Verify SQLite is Available
```python
import sqlite3
print(f"SQLite version: {sqlite3.version}")
print(f"SQLite library version: {sqlite3.sqlite_version}")
```

---

## Key Takeaways for Your Project

| Aspect | Details |
|--------|---------|
| **Database Module** | `sqlite3` (standard library) |
| **ORM Framework** | SQLAlchemy |
| **Database Driver** | Built into Python |
| **Requirements.txt** | Do NOT include sqlite3 |
| **Installation** | `pip install -r requirements.txt` |
| **Database File** | `app/recipe_scaler.db` (auto-created) |

---

## Common Mistakes to Avoid

❌ **WRONG:**
```text
# requirements.txt
sqlite3          # This doesn't exist on PyPI!
```

❌ **WRONG:**
```bash
pip install sqlite3  # Will fail
```

✅ **CORRECT:**
```text
# requirements.txt - Don't include sqlite3 at all
sqlalchemy==2.0.23
```

✅ **CORRECT:**
```python
# Your code
from sqlalchemy import create_engine
import sqlite3  # Use standard library directly

engine = create_engine("sqlite:///./recipe_scaler.db")
```

---

## Final Verification

Run this to confirm everything works:

```python
# test_db.py
import sqlite3
from sqlalchemy import create_engine

# Test 1: Standard library access
print("✓ sqlite3 module available (standard library)")
print(f"  Version: {sqlite3.version}")

# Test 2: SQLAlchemy with SQLite
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
print("✓ SQLAlchemy SQLite engine created successfully")

# Test 3: Database operations
with engine.connect() as conn:
    print("✓ Database connection established")
```

Expected output:
```
✓ sqlite3 module available (standard library)
  Version: 2.6.0
✓ SQLAlchemy SQLite engine created successfully
✓ Database connection established
```

---

## Production Considerations

For final-year projects and professional deployment:

1. **No Special Configuration Needed** - sqlite3 is always available
2. **File-based Storage** - Good for small projects and testing
3. **Consider PostgreSQL** - For production with concurrent users
4. **No Version Conflicts** - sqlite3 version always matches Python
5. **Portable Database** - SQLite databases are single files (easy to backup/transfer)

---

**Status: ✓ Issue Resolved - No Extra Installation Required**
