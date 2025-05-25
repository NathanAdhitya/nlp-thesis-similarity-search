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
    """Combine Dewey and Scholar author datasets into a unified canonical mapping."""
    print("=== Combining Author Datasets ===\n")
    
    # Load both datasets
    dewey_data = load_canonical_data(dewey_file)
    scholar_data = load_canonical_data(scholar_file)
    
    if not dewey_data or not scholar_data:
        print("Failed to load one or both datasets!")
        return
    
    print(f"Loaded Dewey names: {len(dewey_data.get('canonical_mapping', {}))}")
    print(f"Loaded Scholar names: {len(scholar_data.get('canonical_mapping', {}))}")
    
    # Combine all names from both datasets
    all_names = set()
    
    # Add all names from Dewey dataset
    for name in dewey_data.get('canonical_mapping', {}).keys():
        all_names.add(name)
    
    # Add all names from Scholar dataset  
    for name in scholar_data.get('canonical_mapping', {}).keys():
        all_names.add(name)
    
    print(f"Total unique names before clustering: {len(all_names)}")
    
    # Re-cluster all names together
    print(f"Clustering all names with max weighted distance: {cross_match_threshold}")
    unified_clusters = cluster_names_by_similarity(all_names, cross_match_threshold)
    
    print(f"After unified clustering: {len(unified_clusters)} unique canonical names")
    
    # Create unified canonical mapping
    unified_canonical_mapping = {}
    unified_merged_clusters = []
    
    for canonical_name, similar_names in unified_clusters.items():
        # Create mapping for each variant to canonical
        for name in similar_names:
            unified_canonical_mapping[name] = canonical_name
        
        # Only add to merged_clusters if it's actually merged (more than 1 name)
        if len(similar_names) > 1:
            unified_merged_clusters.append({
                "canonical": canonical_name,
                "variants": similar_names,
                "count": len(similar_names)
            })
    
    # Create simplified output data
    output_data = {
        "source": "combined_dewey_scholar",
        "canonical_mapping": unified_canonical_mapping,
        "merged_clusters": unified_merged_clusters,
        "statistics": {
            "total_names": len(all_names),
            "canonical_names": len(unified_clusters),
            "merged_clusters": len(unified_merged_clusters),
            "names_merged": sum(len(cluster["variants"]) - 1 for cluster in unified_merged_clusters),
            "reduction_percentage": round((sum(len(cluster["variants"]) - 1 for cluster in unified_merged_clusters) / len(all_names)) * 100, 2)
        }
    }
    
    # Save unified data
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\nUnified data saved to: {output_file}")
    
    # Show statistics
    print(f"\n=== Unified Dataset Statistics ===")
    print(f"Total input names: {len(all_names)}")
    print(f"Canonical names after clustering: {len(unified_clusters)}")
    print(f"Merged clusters: {len(unified_merged_clusters)}")
    print(f"Names merged: {output_data['statistics']['names_merged']}")
    print(f"Reduction: {output_data['statistics']['reduction_percentage']}%")
    
    # Show sample merged clusters
    print(f"\n=== Sample Merged Clusters ===")
    for i, cluster in enumerate(unified_merged_clusters[:10]):
        print(f"\nCluster {i+1}: '{cluster['canonical']}' ({cluster['count']} variants)")
        for variant in cluster['variants']:
            if variant != cluster['canonical']:
                dist = weighted_name_distance(cluster['canonical'], variant)
                print(f"  - '{variant}' (distance: {dist:.2f})")
    
    return output_data

if __name__ == "__main__":
    dewey_file = "../data/canonical_dewey.json"
    scholar_file = "../data/canonical_scholar.json"
    output_file = "../data/combined_authors.json"
    
    combine_author_datasets(dewey_file, scholar_file, output_file, cross_match_threshold=2.0)
