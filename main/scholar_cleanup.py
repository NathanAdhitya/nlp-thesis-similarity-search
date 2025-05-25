import csv
import json
import os
import re
from collections import defaultdict, Counter
from typing import List, Dict, Tuple, Set
from dewey_cleanup import (
    standardize_name, 
    weighted_name_distance, 
    cluster_names_by_similarity,
    save_canonical_clusters,
    QWERTY_LAYOUT,
    keyboard_distance,
    levenshtein_distance
)

def load_scholar_authors(csv_file: str) -> Set[str]:
    """Load author names from Google Scholar CSV file."""
    author_names = set()
    
    if not os.path.exists(csv_file):
        print(f"File {csv_file} does not exist")
        return author_names
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, 1):
                # Assuming the author name is in a column called 'author' or 'name'
                # Adjust the column name based on your CSV structure
                author_name = row.get('author') or row.get('name') or row.get('Author') or row.get('Name')
                
                if author_name and author_name.strip():
                    # Clean and standardize the name
                    clean_name = clean_scholar_name(author_name.strip())
                    if clean_name and len(clean_name) > 1:
                        author_names.add(clean_name)
                
                if i % 1000 == 0:
                    print(f"Processed {i} scholar records...")
    
    except Exception as e:
        print(f"Error reading {csv_file}: {e}")
        return set()
    
    print(f"Successfully loaded {len(author_names)} unique scholar author names")
    return author_names

def clean_scholar_name(name: str) -> str:
    """Clean Google Scholar author names."""
    if not name:
        return ""
    
    # Remove common academic titles and affiliations
    name = re.sub(r'\b(?:Prof\.?|Dr\.?|PhD\.?|Ph\.D\.?|M\.D\.?|Professor|Dr)\b', '', name, flags=re.IGNORECASE)
    
    # Remove affiliations in parentheses or after dashes
    name = re.sub(r'\([^)]*\)', '', name)
    name = re.sub(r'\s*-\s*.*$', '', name)
    
    # Remove email addresses
    name = re.sub(r'\S+@\S+', '', name)
    
    # Clean up whitespace and punctuation
    name = re.sub(r'\s+', ' ', name).strip()
    name = re.sub(r'[,\.\s]+$', '', name).strip()
    name = re.sub(r'^[,\.\s]+', '', name).strip()
    
    return name

def analyze_scholar_authors(csv_file: str, max_distance: float = 2.0, save_canonical: bool = True):
    """Main function to analyze Google Scholar authors and cluster similar names."""
    print("=== Google Scholar Author Analysis ===\n")
    
    # Load scholar data
    author_names = load_scholar_authors(csv_file)
    if not author_names:
        print("No scholar data found!")
        return
    
    # Standardize all names
    standardized_names = {standardize_name(name) for name in author_names if standardize_name(name)}
    
    print(f"\nBefore clustering: {len(standardized_names)} unique scholar author names")
    
    # Cluster similar names
    print(f"Clustering names with max weighted distance: {max_distance}")
    clusters = cluster_names_by_similarity(standardized_names, max_distance)
    
    print(f"After clustering: {len(clusters)} unique scholar author names")
    
    # Save canonical clusters if requested
    if save_canonical:
        output_file = "../data/canonical_scholar.json"
        
        # Create the canonical mapping
        canonical_mapping = {}
        merged_clusters = []
        
        for canonical_name, similar_names in clusters.items():
            # Create mapping for each variant to canonical
            for name in similar_names:
                canonical_mapping[name] = canonical_name
            
            # Only add to merged_clusters if it's actually merged (more than 1 name)
            if len(similar_names) > 1:
                merged_clusters.append({
                    "canonical": canonical_name,
                    "variants": similar_names
                })
        
        output_data = {
            "source": "google_scholar",
            "canonical_mapping": canonical_mapping,
            "merged_clusters": merged_clusters
        }
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"Scholar canonical clusters saved to: {output_file}")
    
    # Analyze clustering results
    merged_count = sum(1 for cluster in clusters.values() if len(cluster) > 1)
    merged_names = []
    for canonical, similar_names in clusters.items():
        if len(similar_names) > 1:
            merged_names.extend(similar_names[1:])
    
    print(f"\nMerged clusters: {merged_count}")
    print(f"Names that were merged: {len(merged_names)}")
    print(f"Reduction: {len(merged_names)} names ({len(merged_names)/len(standardized_names)*100:.1f}%)")
    
    # Show some merged clusters
    print("\n=== Sample Merged Name Clusters ===")
    merge_count = 0
    for canonical, similar_names in clusters.items():
        if len(similar_names) > 1:
            merge_count += 1
            if merge_count <= 10:  # Show only first 10 clusters
                print(f"\nCluster {merge_count}: '{canonical}'")
                for name in similar_names:
                    if name != canonical:
                        dist = weighted_name_distance(canonical, name)
                        print(f"  - '{name}' (weighted distance: {dist:.2f})")
    
    return {
        'original_count': len(standardized_names),
        'clustered_count': len(clusters),
        'merged_names': merged_names,
        'clusters': clusters
    }

if __name__ == "__main__":
    # Run analysis on Google Scholar data
    csv_file = "../data/authors.csv"
    analyze_scholar_authors(csv_file, max_distance=4.0, save_canonical=True)
