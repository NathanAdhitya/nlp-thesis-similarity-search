import os
from typing import Any
import typing
from dotenv import load_dotenv
from scholarly import scholarly
from scholarly import ProxyGenerator
import csv
import json  # Add json module import

# Set up proxy generator
pg = ProxyGenerator()
success = pg.FreeProxies()
if not success:
    print("Error: Failed to set up proxy generator.")
    exit()
scholarly.use_proxy(pg)

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
                
                # Check if file already exists with more than 200 entries
                output_file = os.path.join(publications_dir, f"{author_id}.jsonl")
                if os.path.exists(output_file):
                    # Count lines in the file to determine number of entries
                    with open(output_file, "r", encoding="utf-8") as f:
                        line_count = sum(1 for _ in f)
                    
                    if line_count > 100:
                        print(f"Skipping author {author_id}: already has {line_count} entries")
                        continue
                    else:
                        print(f"File exists with {line_count} entries, but below threshold. Processing...")
                
                # Get author data
                author = scholarly.search_author_id(author_id)
                
                # Fill author data with publications
                author_data = scholarly.fill(author, sections=['publications'], sortby="year") # type: ignore
                
                if not author_data.get('publications'):
                    print(f"No publications found for author {author_id}")
                    continue
                
                # Prepare output file
                output_file = os.path.join(publications_dir, f"{author_id}.jsonl")  # Changed to .jsonl extension for JSON Lines format
                
                # Open the file at the beginning for JSON Lines writing
                with open(output_file, "w", encoding="utf-8") as f:
                    pub_count = 0
                    
                    for pub in author_data['publications']:
                        try:
                            filled_pub = scholarly.fill(pub, [])
                            
                            # Write this publication as a single JSON line and flush
                            f.write(json.dumps(filled_pub) + '\n')
                            f.flush()
                            pub_count += 1
                            print(".", end='')  # Print a dot for each publication processed
                            
                        except Exception as e:
                            print(f"\nError processing publication: {e}")
                    
                    if pub_count > 0:
                        print(f"\n{pub_count} publications saved to JSON Lines format for author {author_id}")
                    else:
                        print(f"\nNo valid publications to save for author {author_id}")
                
            except Exception as e:
                print(f"Error processing author {author_id}: {e}")
    
    except Exception as e:
        print(f"An error occurred: {e}")

# Execute the scrape function
if __name__ == "__main__":
    print("Starting publication scraping...")
    scrape_author_publications()
    print("Publication scraping complete")