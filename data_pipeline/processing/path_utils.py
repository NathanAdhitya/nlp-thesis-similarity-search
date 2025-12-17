"""
Path utilities for ensuring correct file paths regardless of working directory.
"""
import os
from pathlib import Path


def get_project_root() -> Path:
    """
    Get the project root directory.
    
    Returns:
        Path object pointing to the project root.
    """
    # This file is in data_pipeline/processing/
    # Project root is two levels up
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent
    return project_root


def get_data_path(relative_path: str = "") -> Path:
    """
    Get absolute path to a file/directory in the data folder.
    
    Args:
        relative_path: Path relative to the data directory (e.g., "dewey_thesis" or "authors.csv")
    
    Returns:
        Absolute Path object
    """
    project_root = get_project_root()
    data_dir = project_root / "data"
    
    if relative_path:
        return data_dir / relative_path
    return data_dir


# Convenience functions for common paths
def get_dewey_thesis_dir() -> Path:
    """Get path to dewey_thesis directory."""
    return get_data_path("dewey_thesis")


def get_publications_dir() -> Path:
    """Get path to publications directory."""
    return get_data_path("publications")


def get_canonical_dewey_file() -> Path:
    """Get path to canonical_dewey.json."""
    return get_data_path("canonical_dewey.json")


def get_canonical_scholar_file() -> Path:
    """Get path to canonical_scholar.json."""
    return get_data_path("canonical_scholar.json")


def get_combined_authors_file() -> Path:
    """Get path to combined_authors.json."""
    return get_data_path("combined_authors.json")


def get_merged_authors_file() -> Path:
    """Get path to merged_authors.csv."""
    return get_data_path("merged_authors.csv")


def get_cleaned_dewey_file() -> Path:
    """Get path to cleaned_dewey.csv."""
    return get_data_path("cleaned_dewey.csv")


def get_cleaned_publications_file() -> Path:
    """Get path to cleaned_publications.csv."""
    return get_data_path("cleaned_publications.csv")


def get_authors_csv_file() -> Path:
    """Get path to authors.csv."""
    return get_data_path("authors.csv")


def get_database_file() -> Path:
    """Get path to the main database."""
    return get_data_path("nlp-thesis-similarity-cleaned.db")


if __name__ == "__main__":
    # Test the path utilities
    print("Project root:", get_project_root())
    print("Data directory:", get_data_path())
    print("Dewey thesis directory:", get_dewey_thesis_dir())
    print("Canonical Dewey file:", get_canonical_dewey_file())
    print("Database file:", get_database_file())
