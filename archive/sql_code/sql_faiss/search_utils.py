import json
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Union
from sentence_transformers import SentenceTransformer

def get_embedding(text, model):
    """
    Convert text to embedding using the provided model.
    
    Args:
        text: The text to encode
        model: The SentenceTransformer model to use
        
    Returns:
        List of embedding values or None if text is empty
    """
    # Handle None values or empty strings
    if text is None or text == "":
        return None
    # Convert text to embedding using the provided model
    return model.encode(text).tolist()

def print_formatted_results(results, show_authors=True, show_contributors=True, show_abstract=True, show_metrics=True):
    """
    Print formatted search results with customizable display options
    
    Args:
        results: List of search results from ThesisSimilaritySearch.search()
        show_authors: Whether to display author information
        show_contributors: Whether to display contributor information
        show_abstract: Whether to display the abstract
        show_metrics: Whether to display similarity score and distance
    """
    if not results:
        print("No results found.")
        return
        
    for i, result in enumerate(results):
        print(f"\nResult {i+1}: {result['title']}")
        
        # Display metrics if requested
        if show_metrics:
            print(f"  Similarity: {result['similarity_score']:.4f}")
            print(f"  Distance: {result['distance']:.4f}")
        
        # Display authors if requested
        if show_authors and 'authors' in result:
            if result['authors']:
                authors_str = ", ".join(result['authors'])
                print(f"  Authors: {authors_str}")
            else:
                print(f"  Authors: No author information available")
        
        # Display contributors if requested
        if show_contributors and 'contributors' in result:
            if result['contributors']:
                # Group contributors by role
                contributors_by_role = {}
                for contributor in result['contributors']:
                    role = contributor['role']
                    if role not in contributors_by_role:
                        contributors_by_role[role] = []
                    contributors_by_role[role].append(contributor['name'])
                
                # Print contributors by role
                print(f"  Contributors:")
                for role, names in sorted(contributors_by_role.items()):
                    contributors_str = ", ".join(names)
                    print(f"    {role}: {contributors_str}")
            else:
                print(f"  Contributors: No contributor information available")
        
        # Display abstract if requested
        if show_abstract and 'abstract' in result:
            if result['abstract']:
                # Truncate very long abstracts for display
                abstract = result['abstract']
                if len(abstract) > 300:
                    abstract = abstract[:297] + '...'
                print(f"  Abstract: {abstract}")
            else:
                print(f"  Abstract: No abstract available")

def update_embeddings_in_batches(model, cursor, database, batch_size=100):
    """
    Update embeddings for papers in the database in batches
    
    Args:
        model: The SentenceTransformer model to use for encoding
        cursor: MySQL database cursor
        database: MySQL database connection
        batch_size: Number of papers to process in each batch
    """
    try:
        # First, retrieve all papers that need embeddings
        cursor.execute("""
            SELECT id, title, abstract FROM dewey_papers 
            WHERE (`title_embeddings_all-MiniLM-L6-v2` IS NULL 
            OR `abstract_embeddings_all-MiniLM-L6-v2` IS NULL) 
            AND abstract != ''
        """)
        all_papers = cursor.fetchall()
        
        print(f"Processing {len(all_papers)} papers that need embeddings...")
        
        if not all_papers:
            print("No papers need embeddings. Process complete.")
            return
            
        # Process in batches to avoid memory issues
        total_batches = (len(all_papers) + batch_size - 1) // batch_size
        
        for i in range(0, len(all_papers), batch_size):
            batch = all_papers[i:i+batch_size]
            updates = []
            
            for paper_id, title, abstract in batch:
                title_embedding = get_embedding(title, model)
                abstract_embedding = get_embedding(abstract, model)
                
                if title_embedding is not None or abstract_embedding is not None:
                    updates.append((
                        json.dumps(title_embedding) if title_embedding else None, 
                        json.dumps(abstract_embedding) if abstract_embedding else None, 
                        paper_id
                    ))
            
            # Check if we have any updates to make
            if updates:
                # Update the database with the new embeddings
                update_query = """
                UPDATE dewey_papers 
                SET `title_embeddings_all-MiniLM-L6-v2` = %s, `abstract_embeddings_all-MiniLM-L6-v2` = %s 
                WHERE id = %s
                """
                cursor.executemany(update_query, updates)
                database.commit()
                print(f"Updated embeddings for {len(updates)} papers in batch")
                
    except Exception as e:
        print(f"Error during embedding update: {e}")
        database.rollback()
        raise
