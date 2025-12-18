"""
Centralized configuration for Semantica NLP Thesis Similarity Search System.

This module provides centralized configuration management using environment variables
and sensible defaults. All file paths, model configurations, and application settings
should be imported from here.

Environment Variables:
    - SEMANTICA_DB_PATH: Path to production database (default: data/cleaned_with_bge_m3.db)
    - SEMANTICA_DEVICE: Device for model inference - 'cuda' or 'cpu' (default: auto-detect)
    - API_HOST: Flask API host (default: 0.0.0.0)
    - API_PORT: Flask API port (default: 5000)
    - CORS_ORIGINS: Comma-separated list of allowed origins (default: *)
"""

import os
from pathlib import Path
import torch

# ============================================================================
# Directory Structure
# ============================================================================

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SRC_DIR = BASE_DIR / "src"
ARCHIVE_DIR = BASE_DIR / "archive"

# Data subdirectories (for future organization)
RAW_DATA_DIR = DATA_DIR / "raw"
INTERMEDIATE_DIR = DATA_DIR / "intermediate"
PRODUCTION_DIR = DATA_DIR / "production"

# ============================================================================
# Database Configuration
# ============================================================================

# Production database path (can be overridden via environment variable)
DB_PATH = Path(os.getenv(
    "SEMANTICA_DB_PATH",
    str(DATA_DIR / "cleaned_with_bge_m3.db")
))
DB_PATH_STR = str(DB_PATH)

# ============================================================================
# Model Configuration
# ============================================================================

# Model identifiers for Hugging Face
MODELS = {
    "bgem3": "BAAI/bge-m3",
    "allminilm": "all-MiniLM-L6-v2",
    "indobert": "rahmanfadhil/indobert-finetuned-indonli"
}

# Embedding dimensions for each model
EMBEDDING_DIMS = {
    "bgem3": 1024,
    "allminilm": 384,
    "indobert": 768
}

# Vector table names in database
VECTOR_TABLES = {
    "bgem3": "publications_vec_bge_m3",
    "allminilm": "publications_vec_all_MiniLM_L6_v2",
    "indobert": "publications_vec_indobert"
}

# Device configuration (auto-detect or override)
DEVICE = os.getenv(
    "SEMANTICA_DEVICE",
    "cuda" if torch.cuda.is_available() else "cpu"
)

# ============================================================================
# API Configuration
# ============================================================================

API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "5000"))

# CORS configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
if CORS_ORIGINS != "*":
    CORS_ORIGINS = [origin.strip() for origin in CORS_ORIGINS.split(",")]

# ============================================================================
# Data Pipeline Configuration
# ============================================================================

# Fuzzy matching thresholds
NAME_DISTANCE_THRESHOLD = 2.0  # For author name clustering
CROSS_MATCH_THRESHOLD = 2.0     # For cross-dataset matching

# Scraping configuration
SCRAPER_DELAY = 1.5  # Seconds between requests (rate limiting)
SCRAPER_MAX_RETRIES = 3
SCRAPER_TIMEOUT = 30  # Seconds

# Processing configuration
BATCH_SIZE_EMBEDDING = 100  # Default batch size for embedding generation
DEFAULT_TOP_K = 5  # Default number of search results

# ============================================================================
# Validation
# ============================================================================

def validate_config():
    """Validate configuration and print warnings if needed."""
    if not DB_PATH.exists():
        print(f"WARNING: Database not found at {DB_PATH}")
        print("Run the data pipeline to generate it.")
    
    if DEVICE == "cuda" and not torch.cuda.is_available():
        print("WARNING: CUDA requested but not available. Falling back to CPU.")
    
    return True

# Auto-validate on import
validate_config()
