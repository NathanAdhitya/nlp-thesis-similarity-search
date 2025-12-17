# Archive Directory

**Date Archived:** December 17, 2025  
**Project:** Semantica - NLP Thesis Similarity Search System

---

## Purpose

This directory contains legacy code that has been archived as part of the project reorganization effort. These files are no longer used in the current production system but are preserved for historical reference and potential future use.

**Important:** Do not delete these files. They represent the evolution of the project and may contain useful reference implementations or data processing approaches.

---

## What Was Archived

### 1. SQL-Based Search Engine (`sql_code/`)

**Original Location:** `main/sql_faiss/`

**Contents:**
- `thesis_search_engine.py` - Original SQL/MySQL-based search implementation
- `thesis_search_engine_sqlite.py` - Transition version during SQLite migration
- `search_utils.py` - Legacy search utilities
- `search_by_dosen.ipynb` - Old search interface notebook
- `searching_test.ipynb` - SQL version testing notebook
- `searching_test_sqlite.ipynb` - SQLite transition testing notebook
- `poc_lang-detect.ipynb` - Language detection proof of concept

**Why Archived:**
- System migrated from SQL/MySQL to SQLite with sqlite-vec extension
- FAISS-based vector search replaced by native sqlite-vec functionality
- Current production code uses `main/main/search_engine.py` instead
- Keeping for reference in case we need to understand the original implementation

**Status:** ❌ Deprecated - Not used in production

---

### 2. Proof-of-Concept Notebooks (`pocs/`)

**Original Location:** `main/pocs/`

**Contents:**
- `proof_of_concept_oop.ipynb` - Early OOP-based search engine design
- `proof_of_concept_pandas.ipynb` - Pandas-based data processing experiments

**Why Archived:**
- Early exploration notebooks from project development phase
- Functionality has been integrated into production code
- Useful for understanding design decisions and evolution

**Status:** ⚠️ Historical - Exploration phase work

---

### 3. Old Embedding Notebooks (`old_notebooks/embeddings/`)

**Original Location:** `main/embeddings/`

**Contents:**
- `bge-m3.ipynb` - Early BGE-M3 embedding generation
- `indobert.ipynb` - Early IndoBERT embedding generation

**Why Archived:**
- Redundant with more complete notebooks in `main/sqlite-main/`
- The `main/sqlite-main/generate_embeddings_*.ipynb` notebooks are more comprehensive
- These were early experiments that have been superseded

**Current Production Notebooks:**
- `main/sqlite-main/generate_embeddings.ipynb` (BGE-M3)
- `main/sqlite-main/generate_embeddings_allMiniLM.ipynb` (MiniLM)
- `main/sqlite-main/generate_embeddings_indobert.ipynb` (IndoBERT)

**Status:** ⚠️ Superseded - Use current notebooks instead

---

### 4. Database Building - SQL (`database_building/sql/`)

**Original Location:** `database_building/sql/`

**Contents:**
- `nlp_thesis_similarity.sql` - MySQL database schema
- `faculty_insertion.ipynb` - Faculty data insertion for MySQL
- `program_scraping.ipynb` - Academic program scraping
- `sql_building.ipynb` - SQL database construction notebook
- `erd_sql.png` - Entity-relationship diagram for SQL schema

**Why Archived:**
- System migrated from MySQL to SQLite
- SQL schema no longer matches current production structure
- Current database created by `main/data_processing/cleanup_sqlite.py`
- ERD and schema useful for understanding original design

**Status:** ❌ Deprecated - SQLite used instead

---

### 5. Database Building - SQLite (`database_building/sqlite/`)

**Original Location:** `database_building/sqlite/`

**Contents:**
- `sqlite_embedding_generation_allmini.ipynb` - Early SQLite embedding work

**Why Archived:**
- Directory was mostly empty with only one notebook
- Functionality consolidated into `main/sqlite-main/` notebooks
- Redundant with current embedding generation process

**Status:** ⚠️ Incomplete/Redundant

---

## Directory Structure

```
archive/
├── README.md (this file)
├── sql_code/                          # SQL/FAISS-based search engine
│   └── sql_faiss/
│       ├── thesis_search_engine.py
│       ├── thesis_search_engine_sqlite.py
│       ├── search_utils.py
│       ├── print_formatted_results.py
│       ├── search_by_dosen.ipynb
│       ├── searching_test.ipynb
│       ├── searching_test_sqlite.ipynb
│       └── poc_lang-detect.ipynb
├── pocs/                              # Proof-of-concept notebooks
│   └── pocs/
│       ├── proof_of_concept_oop.ipynb
│       └── proof_of_concept_pandas.ipynb
├── old_notebooks/                     # Redundant notebooks
│   └── embeddings/
│       ├── bge-m3.ipynb
│       └── indobert.ipynb
└── database_building/                 # Old database creation code
    ├── sql/                           # MySQL approach
    │   ├── nlp_thesis_similarity.sql
    │   ├── faculty_insertion.ipynb
    │   ├── program_scraping.ipynb
    │   ├── sql_building.ipynb
    │   └── erd_sql.png
    └── sqlite/                        # Early SQLite work
        └── sqlite_embedding_generation_allmini.ipynb
```

---

## Current Production Code

For reference, here's where to find the current production implementations:

### Search Engine
- **Current:** `main/main/search_engine.py`
- **Archived:** `archive/sql_code/sql_faiss/thesis_search_engine.py`

### Embedding Generation
- **Current:** 
  - `main/sqlite-main/generate_embeddings.ipynb` (BGE-M3)
  - `main/sqlite-main/generate_embeddings_allMiniLM.ipynb` (MiniLM)
  - `main/sqlite-main/generate_embeddings_indobert.ipynb` (IndoBERT)
- **Archived:** `archive/old_notebooks/embeddings/*.ipynb`

### Database Creation
- **Current:** `main/data_processing/cleanup_sqlite.py`
- **Archived:** `archive/database_building/sql/sql_building.ipynb`

### Data Processing
- **Current:** `main/data_processing/authors_cleanup.py` (and related scripts)
- **Archived:** Various notebooks in `archive/pocs/`

---

## When to Reference Archived Code

### Good Reasons to Look at Archived Code:
1. **Understanding design evolution** - See how the system was originally architected
2. **Alternative approaches** - Compare SQL vs SQLite implementations
3. **Historical context** - Understand why certain decisions were made
4. **Data migration** - If you need to migrate from old database formats
5. **Debugging legacy data** - Understanding old data formats or processes

### Bad Reasons to Use Archived Code:
1. ❌ Don't copy archived code into production
2. ❌ Don't base new features on archived implementations
3. ❌ Don't run archived notebooks without understanding they're outdated
4. ❌ Don't assume archived code works with current data/schema

---

## Migration History

### Phase 1: SQL/MySQL → SQLite (Early 2025)
- Migrated from MySQL to SQLite for simpler deployment
- Replaced custom SQL-based vector search with sqlite-vec extension
- Consolidated database schema

### Phase 2: FAISS → sqlite-vec (Mid 2025)
- Removed FAISS dependency
- Integrated vector search directly into SQLite using sqlite-vec
- Improved query performance and simplified architecture

### Phase 3: Code Consolidation (December 2025)
- Archived redundant implementations
- Consolidated notebooks into standard locations
- Cleaned up directory structure

---

## Restoration Instructions

If you need to restore any archived code:

1. **Locate the file** in the appropriate archive subdirectory
2. **Review the code** to understand its dependencies and context
3. **Check compatibility** with current database schema and dependencies
4. **Update as needed** before using in production
5. **Test thoroughly** in a development environment first

**PowerShell Command Example:**
```powershell
# Copy (don't move) a file from archive back to main
Copy-Item -Path "archive/sql_code/sql_faiss/search_utils.py" -Destination "main/utils/" -Force
```

---

## Maintenance Notes

### Do Not Delete This Archive
- Preserves project history
- Reference for design decisions
- Fallback if current approach has issues
- Educational value for understanding evolution

### Git History
All archived files remain in git history:
```powershell
# View history of an archived file
git log --follow -- "archive/sql_code/sql_faiss/thesis_search_engine.py"

# See the file at a specific commit
git show <commit-hash>:main/sql_faiss/thesis_search_engine.py
```

### Disk Space
If disk space becomes an issue, consider:
1. Compressing the archive directory (ZIP)
2. Moving to long-term storage (external drive, cloud)
3. Keeping only in git history (remove from working tree)

**But always keep the git history intact.**

---

## Questions?

If you have questions about archived code:
1. Check `PROJECT_AUDIT.md` for detailed analysis
2. Review `REFACTORING_PLAN.md` for rationale
3. Look at git commit messages for context
4. Compare with current production code

---

**Last Updated:** December 17, 2025  
**Archived By:** Project Refactoring Phase 1  
**Related Documentation:** PROJECT_AUDIT.md, REFACTORING_PLAN.md, PROJECT_SUMMARY.md
