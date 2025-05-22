import os
from typing import Any
import typing
from dotenv import load_dotenv
from scholarly import scholarly
from scholarly import ProxyGenerator
import csv

# Set up proxy generator
pg = ProxyGenerator()
success = pg.FreeProxies()
if not success:
    print("Error: Failed to set up proxy generator.")
    exit()
# scholarly.use_proxy(pg)

# Load environment variables
load_dotenv()

# Define file paths
authors_file = "../data/authors.csv"
publications_dir = "../data/publications"

# Ensure the publications directory exists
os.makedirs(publications_dir, exist_ok=True)

def scrape_author_publications():
    """Scrape publications for each author in authors.csv"""
    if not os.path.exists(authors_file):
        print(f"Error: Authors file not found at {authors_file}")
        return
    
    try:
        # Read profile IDs from authors file
        author_ids = []
        with open(authors_file, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            # Skip header
            next(reader)
            
            for row in reader:
                if row and len(row) > 1 and row[1].strip():  # Assuming scholar_id is in column 1
                    author_ids.append(row[1].strip())
        
        if not author_ids:
            print("No author IDs found in authors file.")
            return
        
        total_authors = len(author_ids)
        print(f"Found {total_authors} authors to process")
        
        for idx, author_id in enumerate(author_ids, 1):
            try:
                print(f"Processing author {idx}/{total_authors}: {author_id}")
                
                # Get author data
                author = scholarly.search_author_id(author_id)
                
                # Fill author data with publications
                author_data = scholarly.fill(author, sections=['publications']) # type: ignore
                
                if not author_data.get('publications'):
                    print(f"No publications found for author {author_id}")
                    continue
                
                # Prepare output file
                output_file = os.path.join(publications_dir, f"{author_id}.csv")
                all_fields = set()
                all_fields.add("bib_publisher")
                
                with open(output_file, "w", newline="", encoding="utf-8") as f:
                    writer = None
                    
                    for pub in author_data['publications']:
                        try:
                            filled_pub = scholarly.fill(pub, [])
                            
                            # Extract main fields and bib fields
                            row_data = {}
                            
                            # Extract top-level fields
                            for key, value in filled_pub.items():
                                if key != 'bib':
                                    if isinstance(value, (dict, list, tuple, set)):
                                        row_data[key] = str(value)
                                    else:
                                        row_data[key] = value
                            
                            # Extract bib fields if available
                            if 'bib' in filled_pub and isinstance(filled_pub['bib'], dict):
                                for key, value in filled_pub['bib'].items():
                                    field_name = f"bib_{key}"
                                    if isinstance(value, (dict, list, tuple, set)):
                                        row_data[field_name] = str(value)
                                    else:
                                        row_data[field_name] = value
                            
                            # Track all fields
                            all_fields.update(row_data.keys())
                            
                            # Initialize writer with fieldnames if not already done
                            if writer is None:
                                fieldnames = sorted(list(all_fields))
                                writer = csv.DictWriter(f, fieldnames=fieldnames)
                                writer.writeheader()
                            
                            # Write and flush publication data
                            writer.writerow(row_data)
                            f.flush()
                        except Exception as e:
                            print(f"Error processing publication: {e}")
                    
                    if writer is None:
                        print(f"No valid publications to save for author {author_id}")
                    else:
                        print(f"Publications saved incrementally for author {author_id}")
                
            except Exception as e:
                print(f"Error processing author {author_id}: {e}")
    
    except Exception as e:
        print(f"An error occurred: {e}")

# Execute the scrape function
if __name__ == "__main__":
    print("Starting publication scraping...")
    scrape_author_publications()
    print("Publication scraping complete")