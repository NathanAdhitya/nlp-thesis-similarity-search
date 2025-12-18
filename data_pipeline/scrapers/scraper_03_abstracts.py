import os
from typing import Any
import typing
from dotenv import load_dotenv
from scholarly import scholarly
from scholarly import ProxyGenerator
import csv
import json
import sys  # Import sys for direct command line argument access

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

def scrape_author_publications(profile_id: str):
    """Scrape publications for a single author by profile_id"""
    try:
        print(f"Processing author: {profile_id}")
        
        # Check if file already exists with more than 20 entries
        output_file = os.path.join(publications_dir, f"{profile_id}.jsonl")
        if os.path.exists(output_file):
            # Count lines in the file to determine number of entries
            with open(output_file, "r", encoding="utf-8") as f:
                line_count = sum(1 for _ in f)
            
            if line_count >= 20:
                print(f"Skipping author {profile_id}: already has {line_count} entries")
                return
            else:
                print(f"File exists with {line_count} entries, but below threshold. Processing...")
        
        # Get author data
        author = scholarly.search_author_id(profile_id)
        
        # Fill author data with publications
        author_data = scholarly.fill(author, sections=['publications'], sortby="year",publication_limit=20) # type: ignore
        
        if not author_data.get('publications'):
            print(f"No publications found for author {profile_id}")
            return
        
        # Prepare output file
        output_file = os.path.join(publications_dir, f"{profile_id}.jsonl")  # Changed to .jsonl extension for JSON Lines format
        
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
                print(f"\n{pub_count} publications saved to JSON Lines format for author {profile_id}")
            else:
                print(f"\nNo valid publications to save for author {profile_id}")
    
    except Exception as e:
        print(f"Error processing author {profile_id}: {e}")

if __name__ == "__main__":
    # Check if a profile_id was provided
    if len(sys.argv) < 2:
        print("Error: No profile_id provided.")
        print("Usage: python 3_scrape_abstracts.py [profile_id]")
        sys.exit(1)
    
    # Get the profile_id from command line argument
    profile_id = sys.argv[1]
    
    print("Starting publication scraping...")
    scrape_author_publications(profile_id)
    print("Publication scraping complete")