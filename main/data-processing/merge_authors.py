import csv
import json
import os
import re
from typing import Dict, Set, List, Optional
from dewey_cleanup import standardize_name

def load_scholar_authors(csv_file: str) -> Dict[str, Dict]:
    """Load scholar authors from CSV file."""
    authors = {}
    
    if not os.path.exists(csv_file):
        print(f"File {csv_file} does not exist")
        return authors
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get('name', '').strip()
            scholar_id = row.get('scholar_id', '').strip()
            
            if name and scholar_id:
                standardized_name = standardize_name(name)
                if standardized_name:
                    authors[standardized_name] = {
                        'original_name': name,
                        'scholar_id': scholar_id,
                        'affiliation': row.get('affiliation', ''),
                        'email_domain': row.get('email_domain', ''),
                        'interests': row.get('interests', ''),
                        'citedby': row.get('citedby', ''),
                        'url_picture': row.get('url_picture', '')
                    }
    
    print(f"Loaded {len(authors)} scholar authors")
    return authors

def load_combined_authors(json_file: str) -> Dict[str, List[str]]:
    """Load combined authors mapping from JSON file."""
    if not os.path.exists(json_file):
        print(f"File {json_file} does not exist")
        return {}
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    canonical_mapping = data.get('canonical_mapping', {})
    print(f"Loaded {len(canonical_mapping)} combined author mappings")
    return canonical_mapping

def merge_authors(scholar_authors: Dict, combined_mapping: Dict, output_file: str):
    """Merge all authors into a unified dataset with IDs."""
    merged_authors = {}
    dewey_id_counter = 1
    
    # Get all unique standardized names from both sources
    all_names = set()
    
    # Add names from scholar authors
    all_names.update(scholar_authors.keys())
    
    # Add names from combined mapping (both keys and values)
    for name, canonical in combined_mapping.items():
        all_names.add(standardize_name(name))
        all_names.add(standardize_name(canonical))
    
    # Remove empty names
    all_names = {name for name in all_names if name and name.strip()}
    
    print(f"Processing {len(all_names)} unique author names")
    
    # Process each unique name
    for name in sorted(all_names):
        if not name:
            continue
            
        # Check if this name maps to a canonical name
        canonical_name = combined_mapping.get(name, name)
        canonical_name = standardize_name(canonical_name)
        
        # Use canonical name as the key
        if canonical_name not in merged_authors:
            # Get scholar info if available
            scholar_info = scholar_authors.get(name) or scholar_authors.get(canonical_name)
            
            merged_authors[canonical_name] = {
                'name': canonical_name,
                'dewey_id': dewey_id_counter,
                'scholar_id': scholar_info.get('scholar_id', '') if scholar_info else '',
                'original_names': [name] if name != canonical_name else [],
                'affiliation': scholar_info.get('affiliation', '') if scholar_info else '',
                'email_domain': scholar_info.get('email_domain', '') if scholar_info else '',
                'interests': scholar_info.get('interests', '') if scholar_info else '',
                'citedby': scholar_info.get('citedby', '') if scholar_info else '',
                'url_picture': scholar_info.get('url_picture', '') if scholar_info else ''
            }
            dewey_id_counter += 1
        else:
            # Add variant name if not already present
            if name != canonical_name and name not in merged_authors[canonical_name]['original_names']:
                merged_authors[canonical_name]['original_names'].append(name)
            
            # Update scholar info if not present but available
            if not merged_authors[canonical_name]['scholar_id'] and name in scholar_authors:
                scholar_info = scholar_authors[name]
                merged_authors[canonical_name].update({
                    'scholar_id': scholar_info.get('scholar_id', ''),
                    'affiliation': scholar_info.get('affiliation', ''),
                    'email_domain': scholar_info.get('email_domain', ''),
                    'interests': scholar_info.get('interests', ''),
                    'citedby': scholar_info.get('citedby', ''),
                    'url_picture': scholar_info.get('url_picture', '')
                })
    
    # Write to CSV
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['name', 'scholar_id', 'dewey_id', 'original_names', 'affiliation', 
                     'email_domain', 'interests', 'citedby', 'url_picture']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for author_data in merged_authors.values():
            # Convert original_names list to string
            author_data['original_names'] = '; '.join(author_data['original_names'])
            writer.writerow(author_data)
    
    print(f"Merged authors saved to: {output_file}")
    print(f"Total merged authors: {len(merged_authors)}")
    
    return merged_authors

if __name__ == "__main__":
    # Load data
    scholar_authors = load_scholar_authors("../data/authors.csv")
    combined_mapping = load_combined_authors("../data/combined_authors.json")
    
    # Merge authors
    merged_authors = merge_authors(scholar_authors, combined_mapping, "../data/merged_authors.csv")
