import json
import os
from typing import Dict, List, Set, Tuple
from dewey_cleanup import (
    standardize_name, 
    weighted_name_distance, 
    cluster_names_by_similarity
)

def load_canonical_data(file_path: str) -> Dict:
    """Load canonical clustering data from JSON file."""
    if not os.path.exists(file_path):
        print(f"File {file_path} does not exist")
        return {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def combine_author_datasets(dewey_file: str, scholar_file: str, output_file: str, cross_match_threshold: float = 2.0):
    """Combine Dewey and Scholar author datasets with cross-matching."""
    print("=== Combining Author Datasets ===\n")
    
    # Load both datasets
    dewey_data = load_canonical_data(dewey_file)
    scholar_data = load_canonical_data(scholar_file)
    
    if not dewey_data or not scholar_data:
        print("Failed to load one or both datasets!")
        return
    
    print(f"Loaded Dewey data: {dewey_data['total_clusters']} clusters")
    print(f"Loaded Scholar data: {scholar_data['total_clusters']} clusters")
    
    # Get all canonical names from both datasets
    dewey_canonicals = set(dewey_data['canonical_mapping'].values())
    scholar_canonicals = set(scholar_data['canonical_mapping'].values())
    
    print(f"Dewey canonical names: {len(dewey_canonicals)}")
    print(f"Scholar canonical names: {len(scholar_canonicals)}")
    
    # Find cross-matches between datasets
    print("\nFinding cross-matches between datasets...")
    cross_matches = []
    
    for i, dewey_name in enumerate(dewey_canonicals):
        if (i + 1) % 100 == 0:
            print(f"Cross-matching {i + 1}/{len(dewey_canonicals)} names...")
        
        for scholar_name in scholar_canonicals:
            distance = weighted_name_distance(dewey_name, scholar_name)
            if distance <= cross_match_threshold:
                cross_matches.append({
                    'dewey_name': dewey_name,
                    'scholar_name': scholar_name,
                    'distance': distance
                })
    
    print(f"Found {len(cross_matches)} cross-matches")
    
    # Create combined canonical mapping
    combined_mapping = {}
    
    # Start with Dewey data
    for name, canonical in dewey_data['canonical_mapping'].items():
        combined_mapping[name] = canonical
    
    # Add Scholar data with prefix to avoid conflicts
    for name, canonical in scholar_data['canonical_mapping'].items():
        # Check if this scholar name matches any dewey name
        matched_dewey = None
        for match in cross_matches:
            if match['scholar_name'] == canonical:
                matched_dewey = match['dewey_name']
                break
        
        if matched_dewey:
            combined_mapping[name] = matched_dewey
        else:
            combined_mapping[name] = canonical
    
    # Create cross-reference clusters
    cross_reference_clusters = []
    matched_dewey = set()
    matched_scholar = set()
    
    for match in cross_matches:
        dewey_canonical = match['dewey_name']
        scholar_canonical = match['scholar_name']
        
        if dewey_canonical not in matched_dewey and scholar_canonical not in matched_scholar:
            # Create a combined cluster
            dewey_variants = [name for name, canonical in dewey_data['canonical_mapping'].items() 
                            if canonical == dewey_canonical]
            scholar_variants = [name for name, canonical in scholar_data['canonical_mapping'].items() 
                              if canonical == scholar_canonical]
            
            cross_cluster = {
                'combined_canonical': dewey_canonical,  # Use Dewey name as primary
                'dewey_canonical': dewey_canonical,
                'scholar_canonical': scholar_canonical,
                'dewey_variants': dewey_variants,
                'scholar_variants': scholar_variants,
                'cross_match_distance': match['distance'],
                'total_variants': len(dewey_variants) + len(scholar_variants)
            }
            
            cross_reference_clusters.append(cross_cluster)
            matched_dewey.add(dewey_canonical)
            matched_scholar.add(scholar_canonical)
    
    # Create output data
    output_data = {
        'metadata': {
            'dewey_source': dewey_file,
            'scholar_source': scholar_file,
            'cross_match_threshold': cross_match_threshold,
            'dewey_clusters': dewey_data['total_clusters'],
            'scholar_clusters': scholar_data['total_clusters'],
            'cross_matches_found': len(cross_matches),
            'combined_clusters': len(cross_reference_clusters)
        },
        'dewey_data': dewey_data,
        'scholar_data': scholar_data,
        'cross_matches': cross_matches,
        'cross_reference_clusters': cross_reference_clusters,
        'combined_mapping': combined_mapping
    }
    
    # Save combined data
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\nCombined data saved to: {output_file}")
    
    # Show statistics
    print(f"\n=== Combined Dataset Statistics ===")
    print(f"Total Dewey clusters: {dewey_data['total_clusters']}")
    print(f"Total Scholar clusters: {scholar_data['total_clusters']}")
    print(f"Cross-reference clusters: {len(cross_reference_clusters)}")
    print(f"Dewey names with Scholar matches: {len(matched_dewey)}")
    print(f"Scholar names with Dewey matches: {len(matched_scholar)}")
    
    # Show sample cross-reference clusters
    print(f"\n=== Sample Cross-Reference Clusters ===")
    for i, cluster in enumerate(cross_reference_clusters[:5]):
        print(f"\nCluster {i+1}:")
        print(f"  Dewey canonical: '{cluster['dewey_canonical']}'")
        print(f"  Scholar canonical: '{cluster['scholar_canonical']}'")
        print(f"  Distance: {cluster['cross_match_distance']:.2f}")
        print(f"  Total variants: {cluster['total_variants']}")
    
    return output_data

if __name__ == "__main__":
    dewey_file = "../data/canonical_dewey.json"
    scholar_file = "../data/canonical_scholar.json"
    output_file = "../data/combined_authors.json"
    
    combine_author_datasets(dewey_file, scholar_file, output_file, cross_match_threshold=2.0)
