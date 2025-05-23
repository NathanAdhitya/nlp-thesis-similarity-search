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
scholarly.use_proxy(pg)

# Load environment variables
load_dotenv()

GS_ORG_ID = os.getenv("GS_ORG_ID") or ""

if not GS_ORG_ID:
    print("Error: GS_ORG_ID environment variable not set.")
    exit()

# Ensure the data directory exists
os.makedirs("../data", exist_ok=True)
output_file = "../data/authors.csv"

# Append to the CSV file if it exists
if os.path.exists(output_file):
    mode = "a"
else:
    mode = "w"
    
def append_manual_authors():
    manual_input_file = "../data/manual_author_import.csv"
    
    if not os.path.exists(manual_input_file):
        print(f"Error: Manual author import file not found at {manual_input_file}")
        return
    
    try:
        # Read profile IDs from manual import file
        profile_ids = []
        with open(manual_input_file, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            # Skip header if exists
            try:
                next(reader)
            except StopIteration:
                pass
            
            for row in reader:
                if row and row[0].strip():
                    profile_ids.append(row[0].strip())
        
        if not profile_ids:
            print("No profile IDs found in import file.")
            return
            
        # Open CSV file for appending
        with open(output_file, mode, newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            
            # Write header if creating new file
            if mode == "w":
                header = [
                    "name",
                    "scholar_id",
                    "affiliation",
                    "email_domain",
                    "interests",
                    "citedby",
                    "url_picture",
                ]
                writer.writerow(header)
            
            count = 0
            for profile_id in profile_ids:
                try:
                    print(f"Fetching author with ID: {profile_id}")
                    author = scholarly.search_author_id(profile_id)
                    
                    # Extract relevant fields
                    row = [
                        author.get("name", ""),
                        author.get("scholar_id", ""),
                        author.get("affiliation", ""),
                        author.get("email_domain", ""),
                        ";".join(author.get("interests", [])),
                        author.get("citedby", 0),
                        author.get("url_picture", ""),
                    ]
                    
                    # Write the row and flush
                    writer.writerow(row)
                    f.flush()
                    
                    count += 1
                    print(f"Added author: {author.get('name', 'Unknown')}")
                    
                except Exception as e:
                    print(f"Error fetching author with ID {profile_id}: {e}")
            
            print(f"Finished importing. Added {count} authors.")
    
    except Exception as e:
        print(f"An error occurred: {e}")

# Execute the import function
if __name__ == "__main__":
    print("Starting manual author import...")
    append_manual_authors()
    print(f"Results saved to {output_file}")