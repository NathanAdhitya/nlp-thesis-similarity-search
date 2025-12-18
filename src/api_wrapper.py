"""
API wrapper for the SearchEngine with JSON serialization utilities.

This module provides a simple interface for the Flask API to interact with
the SearchEngine, handling both thesis and advisor searches with proper
type conversion for JSON serialization.
"""

from typing import List, Dict, Any, Optional, Union
import numpy as np

from src.search_engine import SearchEngine

# Initialize search engine singleton
search_engine = SearchEngine()


def search(
    query: str, 
    thesis: bool = True, 
    top_k: int = 10, 
    option: str = "bgem3", 
    program_ids: Optional[List[int]] = None
) -> List[Dict[str, Any]]:
    """
    Perform a search for either thesis papers or advisors.
    
    Args:
        query: The search query string.
        thesis: If True, search for papers; if False, search for advisors.
        top_k: Number of top results to return.
        option: Embedding model to use ('bgem3', 'allminilm', or 'indobert').
        program_ids: Optional list of program IDs to filter advisors (only used when thesis=False).
        
    Returns:
        List of dictionaries containing search results, JSON-serializable.
    """
    if thesis:
        results = search_engine.search_thesis(
            query=query, top_k=top_k, option=option)
    else:
        results = search_engine.search_advisor_3(
            query=query,
            top_k=top_k,
            option=option,
            program_ids=program_ids
        )

    return convert_to_json_serializable(results)


def get_all_programs() -> List[Dict[str, Any]]:
    """
    Get all available programs from the database.
    
    Returns:
        List of dictionaries containing program information.
    """
    return search_engine.get_all_programs()


def convert_to_json_serializable(obj: Any) -> Any:
    """
    Recursively convert NumPy types to native Python types for JSON serialization.
    
    Args:
        obj: Object to convert (can be dict, list, numpy types, or primitives).
        
    Returns:
        JSON-serializable version of the input object.
    """
    if isinstance(obj, dict):
        return {k: convert_to_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_json_serializable(i) for i in obj]
    elif isinstance(obj, (np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, (np.int32, np.int64)):
        return int(obj)
    else:
        return obj
