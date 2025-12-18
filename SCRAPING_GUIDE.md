# Data Pipeline Guide

Process scraped data into production database for Semantica.

## Prerequisites

- Python 3.8+
- Install dependencies: `pip install -r requirements.txt`
- Scraped data in `data/` directory

## Quick Start

```bash
python data_pipeline/processing/run_pipeline.py
```

Scripts automatically skip if output files exist. Delete outputs to force regeneration.

## Pipeline Overview

```
Raw Data → Clean → Combine → Merge → Extract → Database
```

### Input (Expected, after scraping)
- `data/dewey_thesis/*.json` - ~41,597 thesis files
- `data/publications/*.jsonl` - ~217 author publication files
- `data/dewey_thesis_data.csv` - Collection metadata

### Processing Steps

**Step 1: Dewey Cleanup** - `step_01_dewey_cleanup.py`
- Cleans author names, removes titles, clusters duplicates
- Output: `data/canonical_dewey.json`

**Step 2: Scholar Cleanup** - `step_02_scholar_cleanup.py`
- Cleans Google Scholar names, clusters variants
- Output: `data/canonical_scholar.json`

**Step 3: Combine Authors** - `step_03_combine_authors.py`
- Cross-matches Dewey and Scholar datasets
- Output: `data/combined_authors.json`

**Step 4: Merge Authors** - `step_04_merge_authors.py`
- Assigns unique IDs, creates CSV
- Output: `data/merged_authors.csv`

**Step 5: Extract Publications** - `step_05_extract_publications.py`
- Extracts publications with author mappings
- Output: `data/cleaned_publications.csv`, `data/cleaned_dewey.csv`

**Step 6: Create Database** - `step_06_create_database.py`
- Creates SQLite database with all data
- Output: `data/nlp-thesis-similarity-cleaned.db`

### Output Database (expected)

**Tables:**
- `users` - 1,580 author profiles
- `publications` - 45,499 papers and theses
- `publication_user_mapping` - 67,843 relationships

**Sample Queries:**
```sql
-- Author's publications
SELECT p.* FROM publications p
JOIN publication_user_mapping pum ON p.id = pum.publication_id
WHERE pum.user_id = 123;

-- Co-authors
SELECT u.name FROM users u
JOIN publication_user_mapping pum ON u.id = pum.user_id
WHERE pum.publication_id = 456;
```

## Individual Step Execution

Run from project root:
```bash
python data_pipeline/processing/step_01_dewey_cleanup.py
python data_pipeline/processing/step_02_scholar_cleanup.py
python data_pipeline/processing/step_03_combine_authors.py
python data_pipeline/processing/step_04_merge_authors.py
python data_pipeline/processing/step_05_extract_publications.py
python data_pipeline/processing/step_06_create_database.py
```

## Regenerating Data

```bash
# Windows
Remove-Item data\canonical_*.json, data\combined_authors.json, data\merged_authors.csv, data\cleaned_*.csv, data\nlp-thesis-similarity-cleaned.db

# Linux/macOS
rm data/{canonical_*.json,combined_authors.json,merged_authors.csv,cleaned_*.csv,nlp-thesis-similarity-cleaned.db}
```

## Scraping (Reference)

Scripts in `data_pipeline/scrapers/`:

- `scraper_01_gs_authors.py` - Google Scholar authors by organization
- `scraper_02_gs_manual.py` - Manual author import
- `scraper_03_abstracts.py` - Publication abstracts (via `run_scrapers.py`)
- `scraper_04_dewey_collection.py` - Thesis collection metadata
- `scraper_05_dewey_theses.py` - Detailed thesis data
- `run_scrapers.py` - Parallel execution for scraper_03

**Setup:** Create `.env` in `data_pipeline/scrapers/`:
```
GS_ORG_ID=your_organization_id
```

## Troubleshooting

**Module not found:** `pip install -r requirements.txt`

**Output already exists:** Scripts skip automatically. Delete files to regenerate.

**Database exists:** Delete `data/nlp-thesis-similarity-cleaned.db` to recreate.
