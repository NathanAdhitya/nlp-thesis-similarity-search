import os
import csv
import subprocess
from concurrent.futures import ThreadPoolExecutor

# Define file paths
authors_file = "../data/authors.csv"
script_path = os.path.join(os.path.dirname(__file__), "3_scrape_abstracts.py")

def get_profile_ids():
    """Read profile IDs from the authors file."""
    profile_ids = []
    if not os.path.exists(authors_file):
        print(f"Error: Authors file not found at {authors_file}")
        return profile_ids
    
    with open(authors_file, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row in reader:
            if row and len(row) > 1 and row[1].strip():  # Assuming scholar_id is in column 1
                profile_ids.append(row[1].strip())
    return profile_ids

def run_scraper(profile_id: str):
    """Run the scraper script for a single profile ID."""
    try:
        subprocess.run(["python", script_path, profile_id], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running scraper for profile ID {profile_id}: {e}")

if __name__ == "__main__":
    # Get profile IDs from authors file
    profile_ids = get_profile_ids()
    if not profile_ids:
        print("No profile IDs found. Exiting.")
        exit()
    
    # Run up to 8 scrapers in parallel
    with ThreadPoolExecutor(max_workers=8) as executor:
        executor.map(run_scraper, profile_ids)
