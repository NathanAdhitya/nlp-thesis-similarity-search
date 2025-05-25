import csv
import json
import os
import re
from typing import Dict, List, Optional, Tuple
from dewey_cleanup import standardize_name, extract_contributor_info, is_advisor_role

def extract_year_from_source(source: str) -> Optional[str]:
    """Extract year from source field."""
    if not source:
        return None
    
    # Look for 4-digit year patterns
    year_patterns = [
        r'/(\d{4})[,\s]',  # Pattern like "/2001,"
        r'No\.\d+/[^/]+/(\d{4})',  # Pattern like "No.003/EP-IHM/2001"
        r'(\d{4})',  # Any 4-digit number (last resort)
        r'\d+/.+?/(\d{4})',# Pattern: 36020756/MAN/2020
    ]
    
    for pattern in year_patterns:
        match = re.search(pattern, source)
        if match:
            year = match.group(1)
            # Validate year is reasonable (between 1950 and 2030)
            if 1950 <= int(year) <= 2030:
                return year
    
    return None

def load_merged_authors(csv_file: str) -> Tuple[Dict[str, Dict], Dict[str, Dict]]:
    """Load merged authors to get name-to-ID mappings."""
    name_to_dewey_id = {}
    name_to_scholar_id = {}
    
    if not os.path.exists(csv_file):
        print(f"Merged authors file {csv_file} not found")
        return {}, {}
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row['name']
            dewey_id = row['dewey_id']
            scholar_id = row['scholar_id']
            original_names = row.get('original_names', '').split('; ') if row.get('original_names') else []
            
            # Map canonical name
            name_to_dewey_id[name] = dewey_id
            if scholar_id:
                name_to_scholar_id[name] = scholar_id
            
            # Map original names
            for orig_name in original_names:
                if orig_name.strip():
                    name_to_dewey_id[orig_name.strip()] = dewey_id
                    if scholar_id:
                        name_to_scholar_id[orig_name.strip()] = scholar_id
    
    return name_to_dewey_id, name_to_scholar_id

def extract_dewey_thesis_data(data_dir: str, name_to_dewey_id: Dict, output_file: str):
    """Extract thesis data from Dewey thesis files."""
    thesis_data = []
    thesis_id = 1
    
    if not os.path.exists(data_dir):
        print(f"Directory {data_dir} does not exist")
        return
    
    json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
    print(f"Processing {len(json_files)} thesis files...")
    
    for i, filename in enumerate(json_files, 1):
        filepath = os.path.join(data_dir, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                if not data:
                    continue
                
                # Extract basic information
                title = data.get('title', '').strip()
                abstract = data.get('abstract', '').strip()
                source = data.get('source', '').strip()
                contributors_text = data.get('contributors', '')
                
                # Extract year from source
                year = extract_year_from_source(source)
                
                # Extract advisor dewey IDs
                dewey_ids = []
                if contributors_text:
                    contributors = extract_contributor_info(contributors_text)
                    for contributor in contributors:
                        if is_advisor_role(contributor['role']):
                            clean_name = contributor['clean_name']
                            if clean_name:
                                standardized_name = standardize_name(clean_name)
                                if standardized_name in name_to_dewey_id:
                                    dewey_id = name_to_dewey_id[standardized_name]
                                    if dewey_id not in dewey_ids:
                                        dewey_ids.append(dewey_id)
                
                thesis_data.append({
                    'thesis_id': thesis_id,
                    'dewey_ids': '; '.join(dewey_ids),
                    'year': year or '',
                    'title': title,
                    'abstract': abstract
                })
                
                thesis_id += 1
                
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error reading {filename}: {e}")
        
        if i % 1000 == 0:
            print(f"Processed {i}/{len(json_files)} files...")
    
    # Write to CSV
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['thesis_id', 'dewey_ids', 'year', 'title', 'abstract']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(thesis_data)
    
    print(f"Extracted {len(thesis_data)} thesis records to {output_file}")

def extract_publication_data(data_dir: str, name_to_scholar_id: Dict, output_file: str):
    """Extract publication data from publications folder."""
    if not os.path.exists(data_dir):
        print(f"Publications directory {data_dir} does not exist")
        return
    
    publication_data = []
    pub_id = 1
    
    # Look for JSONL files in publications directory
    jsonl_files = []
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith('.jsonl'):
                jsonl_files.append(os.path.join(root, file))
    
    print(f"Processing {len(jsonl_files)} publication files...")
    
    # Create reverse mapping from scholar_id to names for author matching
    scholar_id_to_names = {}
    for name, scholar_id in name_to_scholar_id.items():
        if scholar_id not in scholar_id_to_names:
            scholar_id_to_names[scholar_id] = []
        scholar_id_to_names[scholar_id].append(name)
    
    for i, filepath in enumerate(jsonl_files, 1):
        try:
            # Extract scholar_id from filename
            filename = os.path.basename(filepath)
            file_scholar_id = filename.replace('.jsonl', '')
            
            with open(filepath, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        pub = json.loads(line.strip())
                        
                        if not isinstance(pub, dict):
                            continue
                        
                        # Extract publication info from bib section
                        bib = pub.get('bib', {})
                        if not bib:
                            continue
                        
                        title = bib.get('title', '').strip()
                        abstract = bib.get('abstract', '').strip()
                        year = bib.get('pub_year', '') or pub.get('year', '')
                        
                        # Extract authors from the author string
                        author_string = bib.get('author', '')
                        scholar_ids = []
                        
                        if author_string:
                            # Parse author string (usually "Author1 and Author2 and Author3")
                            authors = [author.strip() for author in re.split(r'\s+and\s+', author_string)]
                            
                            for author in authors:
                                if author:
                                    standardized_name = standardize_name(author)
                                    if standardized_name in name_to_scholar_id:
                                        scholar_id = name_to_scholar_id[standardized_name]
                                        if scholar_id not in scholar_ids:
                                            scholar_ids.append(scholar_id)
                        
                        # If no scholar IDs found from author names, use the file's scholar_id
                        # This ensures we don't lose publications even if name matching fails
                        if not scholar_ids and file_scholar_id in scholar_id_to_names:
                            scholar_ids.append(file_scholar_id)
                            
                        # Strip newlines from title and abstract
                        title = title.replace('\n', ' ').strip()
                        abstract = abstract.replace('\n', ' ').strip()
                        
                        # Strip excessive whitespace
                        title = re.sub(r'\s+', ' ', title)
                        abstract = re.sub(r'\s+', ' ', abstract)
                        
                        publication_data.append({
                            'pub_id': pub_id,
                            'scholar_ids': '; '.join(scholar_ids),
                            'year': str(year) if year else '',
                            'title': title,
                            'abstract': abstract
                        })
                        
                        pub_id += 1
                        
                    except json.JSONDecodeError as e:
                        print(f"Error parsing line {line_num} in {filepath}: {e}")
                        continue
                        
        except (FileNotFoundError, UnicodeDecodeError) as e:
            print(f"Error reading {filepath}: {e}")
        
        if i % 100 == 0:
            print(f"Processed {i}/{len(jsonl_files)} files...")
    
    # Write to CSV
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['pub_id', 'scholar_ids', 'year', 'title', 'abstract']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(publication_data)
    
    print(f"Extracted {len(publication_data)} publication records to {output_file}")

if __name__ == "__main__":
    # Load merged authors for ID mapping
    name_to_dewey_id, name_to_scholar_id = load_merged_authors("../data/merged_authors.csv")
    
    print(f"Loaded {len(name_to_dewey_id)} name-to-dewey-ID mappings")
    print(f"Loaded {len(name_to_scholar_id)} name-to-scholar-ID mappings")
    
    # Extract thesis data
    extract_dewey_thesis_data("../data/dewey_thesis", name_to_dewey_id, "../data/cleaned_dewey.csv")
    
    # Extract publication data
    extract_publication_data("../data/publications", name_to_scholar_id, "../data/cleaned_publications.csv")
