import json
import os
import re
from collections import defaultdict, Counter
from typing import List, Dict, Tuple, Set
import difflib

# QWERTY keyboard layout for calculating keyboard distance
QWERTY_LAYOUT = {
    'q': (0, 0), 'w': (0, 1), 'e': (0, 2), 'r': (0, 3), 't': (0, 4), 'y': (0, 5), 'u': (0, 6), 'i': (0, 7), 'o': (0, 8), 'p': (0, 9),
    'a': (1, 0), 's': (1, 1), 'd': (1, 2), 'f': (1, 3), 'g': (1, 4), 'h': (1, 5), 'j': (1, 6), 'k': (1, 7), 'l': (1, 8),
    'z': (2, 0), 'x': (2, 1), 'c': (2, 2), 'v': (2, 3), 'b': (2, 4), 'n': (2, 5), 'm': (2, 6)
}

def extract_contributor_info(contributors_text: str) -> List[Dict[str, str]]:
    """
    Extract contributor names, clean titles, and identify roles from contributors text.
    
    Args:
        contributors_text: Raw contributors string from JSON
        
    Returns:
        List of dictionaries with 'name', 'clean_name', and 'role' keys
    """
    if not contributors_text or contributors_text.strip() == "":
        return []
    
    # Split by semicolon to get individual contributors
    contributors = [c.strip() for c in contributors_text.split(';') if c.strip()]
    
    result = []
    
    for contributor in contributors:
        # Extract role (text in parentheses at the end)
        role_match = re.search(r'\(([^)]+)\)$', contributor)
        role = role_match.group(1) if role_match else "Unknown"
        
        # Remove role from name
        name_part = re.sub(r'\s*\([^)]+\)$', '', contributor).strip()
        
        # Simplified title cleaning - just take everything before the first comma
        if ',' in name_part:
            potential_name = name_part.split(',')[0].strip()
        else:
            potential_name = name_part
        
        # Enhanced cleanup for titles that might be space-separated or at the beginning
        titles_pattern = r'\b(?:Prof\.?|Dr\.?|Ir\.?|Dra\.?|Drs\.?|S\.T\.?|M\.T\.?|M\.Eng\.?|M\.Sc\.?|M\.A\.?|M\.S\.?|M\.Si\.?|M\.Kom\.?|M\.Hum\.?|M\.Pd\.?|Ph\.D\.?)\b'
        
        clean_name = re.sub(titles_pattern, '', potential_name, flags=re.IGNORECASE)
        
        # Clean up extra whitespace, commas, and periods
        clean_name = re.sub(r'\s+', ' ', clean_name).strip()
        clean_name = re.sub(r'[,\.\s]+$', '', clean_name).strip()
        clean_name = re.sub(r'^[,\.\s]+', '', clean_name).strip()
        
        # Additional check: if the result is empty or very short, try to extract a proper name
        if not clean_name or len(clean_name.strip()) <= 2:
            # Split the original potential_name and try to find the actual name part
            words = potential_name.split()
            name_words = []
            for word in words:
                # Skip obvious title words
                if not re.match(titles_pattern, word, flags=re.IGNORECASE):
                    name_words.append(word)
            clean_name = ' '.join(name_words).strip()
        
        result.append({
            'name': name_part,
            'clean_name': clean_name,
            'role': role
        })
    
    return result

def is_advisor_role(role: str) -> bool:
    """Check if a role indicates the person is an advisor."""
    advisor_keywords = ['advisor', 'adviser', 'supervisor', 'promotor', 'pembimbing']
    return any(keyword in role.lower() for keyword in advisor_keywords)

def load_thesis_data(data_dir: str) -> List[Dict]:
    """Load all thesis JSON files from the data directory."""
    thesis_data = []
    
    if not os.path.exists(data_dir):
        print(f"Directory {data_dir} does not exist")
        return thesis_data
    
    json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
    print(f"Found {len(json_files)} JSON files")
    
    for i, filename in enumerate(json_files, 1):
        filepath = os.path.join(data_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data:  # Only add non-empty files
                    thesis_data.append(data)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error reading {filename}: {e}")
        
        # Progress reporting every 1000 files
        if i % 1000 == 0:
            print(f"Processed {i}/{len(json_files)} files...")
    
    print(f"Successfully loaded {len(thesis_data)} thesis records")
    return thesis_data

def extract_advisor_names(thesis_data: List[Dict]) -> Set[str]:
    """Extract all unique advisor names from thesis data."""
    advisor_names = set()
    total_records = len(thesis_data)
    
    for i, thesis in enumerate(thesis_data, 1):
        contributors_text = thesis.get('contributors', '')
        contributors = extract_contributor_info(contributors_text)
        
        for contributor in contributors:
            if is_advisor_role(contributor['role']):
                clean_name = contributor['clean_name']
                if clean_name and len(clean_name.strip()) > 1:  # Filter out very short names
                    advisor_names.add(clean_name.strip())
        
        # Progress reporting every 1000 records
        if i % 1000 == 0:
            print(f"Processed {i}/{total_records} thesis records...")
    
    return advisor_names

def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

def keyboard_distance(char1: str, char2: str) -> float:
    """Calculate the physical distance between two keys on a QWERTY keyboard."""
    char1, char2 = char1.lower(), char2.lower()
    
    if char1 not in QWERTY_LAYOUT or char2 not in QWERTY_LAYOUT:
        return 2.0  # High penalty for non-keyboard characters
    
    pos1 = QWERTY_LAYOUT[char1]
    pos2 = QWERTY_LAYOUT[char2]
    
    # Euclidean distance between key positions
    return ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5

def standardize_name(name: str) -> str:
    """Standardize name format for consistent comparison."""
    if not name:
        return ""
    
    # Convert to title case and remove extra whitespace
    standardized = ' '.join(name.strip().split()).title()
    
    # Handle common Indonesian name patterns
    # Convert single letters followed by periods to proper initials
    standardized = re.sub(r'\b([A-Z])\.\s*([A-Z])\b', r'\1. \2', standardized)
    
    return standardized

def weighted_name_distance(name1: str, name2: str, keyboard_weight: float = 0.3) -> float:
    """
    Calculate weighted distance considering both Levenshtein and keyboard distance.
    
    Args:
        name1, name2: Names to compare
        keyboard_weight: Weight for keyboard distance (0-1)
        
    Returns:
        Weighted distance score
    """
    if not name1 or not name2:
        return float('inf')
    
    # Standardize names for comparison
    std_name1 = standardize_name(name1).lower()
    std_name2 = standardize_name(name2).lower()
    
    # Quick check for identical names
    if std_name1 == std_name2:
        return 0.0
    
    # Calculate basic Levenshtein distance
    lev_distance = levenshtein_distance(std_name1, std_name2)
    
    # If names are very different in length, likely not the same person
    len_diff = abs(len(std_name1) - len(std_name2))
    if len_diff > max(len(std_name1), len(std_name2)) * 0.5:
        return lev_distance + 10  # Heavy penalty
    
    # Calculate keyboard-aware penalty for character substitutions
    keyboard_penalty = 0.0
    min_len = min(len(std_name1), len(std_name2))
    
    # Compare character by character for keyboard distance
    for i in range(min_len):
        if std_name1[i] != std_name2[i]:
            kb_dist = keyboard_distance(std_name1[i], std_name2[i])
            # High keyboard distance suggests intentional difference, not typo
            if kb_dist > 1.5:  # Keys far apart
                keyboard_penalty += 2.0
            else:
                keyboard_penalty += kb_dist * 0.5
    
    # Combine Levenshtein distance with keyboard penalty
    total_distance = lev_distance + (keyboard_penalty * keyboard_weight)
    
    return total_distance

def cluster_names_by_similarity(names: Set[str], max_distance: float = 2.0) -> Dict[str, List[str]]:
    """
    Cluster names based on weighted distance considering keyboard layout.
    
    Args:
        names: Set of names to cluster
        max_distance: Maximum weighted distance for clustering
        
    Returns:
        Dictionary mapping canonical name to list of similar names
    """
    names_list = list(names)
    clusters = {}
    used_names = set()
    total_names = len(names_list)
    
    for i, name1 in enumerate(names_list):
        if name1 in used_names:
            continue
            
        cluster = [name1]
        used_names.add(name1)
        
        for j, name2 in enumerate(names_list[i+1:], i+1):
            if name2 in used_names:
                continue
            
            # Calculate weighted distance
            distance = weighted_name_distance(name1, name2)
            
            # Additional check for word-level similarity in multi-word names
            # name1_words = standardize_name(name1).split()
            # name2_words = standardize_name(name2).split()
            
            # # If both names have multiple words, check if they share significant words
            # if len(name1_words) > 1 and len(name2_words) > 1:
            #     common_words = 0
            #     for word1 in name1_words:
            #         for word2 in name2_words:
            #             if weighted_name_distance(word1, word2) <= 1.5:
            #                 common_words += 1
            #                 break
                
            #     # If most words match, consider it a match regardless of total distance
            #     if common_words >= min(len(name1_words), len(name2_words)) - 1:
            #         distance = min(distance, max_distance - 0.1)
            
            if distance <= max_distance:
                cluster.append(name2)
                used_names.add(name2)
        
        # Use standardized form of the longest name as canonical
        canonical_name = max(cluster, key=lambda x: (len(standardize_name(x)), standardize_name(x)))
        clusters[standardize_name(canonical_name)] = [standardize_name(name) for name in cluster]
        
        # Progress reporting every 1000 names processed
        if (i + 1) % 100 == 0:
            print(f"Clustered {i + 1}/{total_names} names...")
    
    return clusters

def save_canonical_clusters(clusters: Dict[str, List[str]], output_file: str):
    """Save clustering results to a JSON file."""
    # Create the canonical mapping
    canonical_mapping = {}
    merged_clusters = []
    
    for canonical_name, similar_names in clusters.items():
        # Create mapping for each variant to canonical (including single-name clusters)
        for name in similar_names:
            canonical_mapping[name] = canonical_name
        
        # Only add to merged_clusters if it's actually merged (more than 1 name)
        if len(similar_names) > 1:
            merged_clusters.append({
                "canonical": canonical_name,
                "variants": similar_names
            })
    
    output_data = {
        "source": "dewey_thesis",
        "canonical_mapping": canonical_mapping,
        "merged_clusters": merged_clusters
    }
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"Canonical clusters saved to: {output_file}")

def analyze_thesis_advisors(data_dir: str, max_distance: float = 2.0, save_canonical: bool = True):
    """Main function to analyze thesis advisors and cluster similar names."""
    print("=== Thesis Advisor Analysis ===\n")
    
    # Load thesis data
    thesis_data = load_thesis_data(data_dir)
    if not thesis_data:
        print("No thesis data found!")
        return
    
    # Extract advisor names
    print("Extracting advisor names...")
    advisor_names = extract_advisor_names(thesis_data)
    
    # Standardize all names
    standardized_names = {standardize_name(name) for name in advisor_names if standardize_name(name)}
    
    print(f"\nBefore clustering: {len(standardized_names)} unique advisor names")
    
    # Cluster similar names
    print(f"Clustering names with max weighted distance: {max_distance}")
    clusters = cluster_names_by_similarity(standardized_names, max_distance)
    
    print(f"After clustering: {len(clusters)} unique advisor names")
    
    # Save canonical clusters if requested
    if save_canonical:
        output_file = "../data/canonical_dewey.json"
        save_canonical_clusters(clusters, output_file)
    
    # Analyze clustering results
    merged_count = sum(1 for cluster in clusters.values() if len(cluster) > 1)
    merged_names = []
    for canonical, similar_names in clusters.items():
        if len(similar_names) > 1:
            merged_names.extend(similar_names[1:])  # All except canonical
    
    print(f"\nMerged clusters: {merged_count}")
    print(f"Names that were merged: {len(merged_names)}")
    print(f"Reduction: {len(merged_names)} names ({len(merged_names)/len(standardized_names)*100:.1f}%)")
    
    # Show merged clusters
    print("\n=== Merged Name Clusters ===")
    merge_count = 0
    for canonical, similar_names in clusters.items():
        if len(similar_names) > 1:
            merge_count += 1
            print(f"\nCluster {merge_count}: '{canonical}'")
            for name in similar_names:
                if name != canonical:
                    dist = weighted_name_distance(canonical, name)
                    print(f"  - '{name}' (weighted distance: {dist:.2f})")
    
    # Show some statistics
    print(f"\n=== Statistics ===")
    print(f"Total thesis records: {len(thesis_data)}")
    print(f"Original unique advisor names: {len(standardized_names)}")
    print(f"Clustered unique advisor names: {len(clusters)}")
    print(f"Names merged into clusters: {len(merged_names)}")
    print(f"Number of clusters with merges: {sum(1 for cluster in clusters.values() if len(cluster) > 1)}")
    
    # Show disappeared names (merged ones)
    if merged_names:
        print(f"\n=== Names that disappeared after clustering ===")
        for i, name in enumerate(sorted(merged_names), 1):
            print(f"{i:3d}. {name}")
    
    return {
        'original_count': len(standardized_names),
        'clustered_count': len(clusters),
        'merged_names': merged_names,
        'clusters': clusters
    }

if __name__ == "__main__":
    # Test the contributor extraction function
    test_contributors = [
        "Prof. Dr. John Smith, M.T. (Advisor 1); Jane Doe, S.T., M.Sc. (Examination Committee 1)",
        "Andreas Handojo (Advisor 1); Adi Wibowo, S.T., M.T., Ph.D. (Advisor 2)",
        "Dr. Ir. Lintu Tulistyantoro, M.Ds. (Advisor 1); Grace Setiati, S.Sn., M.Ds. (Examination Committee 1)"
    ]
    
    print("=== Testing Contributor Extraction ===")
    for i, test in enumerate(test_contributors, 1):
        print(f"\nTest {i}: {test}")
        result = extract_contributor_info(test)
        for contrib in result:
            print(f"  Name: '{contrib['name']}' -> Clean: '{contrib['clean_name']}' | Role: {contrib['role']}")
    
    # Test keyboard distance and name standardization
    print("\n=== Testing Keyboard Distance ===")
    test_pairs = [
        ("RENDI", "Andi"),
        ("Rudy Setiawan", "Budi Setiawan"),
        ("John Smith", "Jon Smith"),
        ("Andreas", "Andraes"),
        ("Maria", "Mario")
    ]
    
    for name1, name2 in test_pairs:
        dist = weighted_name_distance(name1, name2)
        std1, std2 = standardize_name(name1), standardize_name(name2)
        print(f"'{name1}' vs '{name2}': {dist:.2f} (standardized: '{std1}' vs '{std2}')")
    
    print("\n" + "="*50 + "\n")
    
    # Run main analysis
    data_directory = "../data/dewey_thesis"
    analyze_thesis_advisors(data_directory, max_distance=4.0, save_canonical=True)
