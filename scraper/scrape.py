import os
from dotenv import load_dotenv
from scholarly import scholarly
import csv

load_dotenv()
GS_ORG_ID = os.getenv("GS_ORG_ID")

if not GS_ORG_ID:
    print("Error: GS_ORG_ID environment variable not set.")
    exit()

# Ensure the data directory exists
os.makedirs("../data", exist_ok=True)
output_file = "../data/authors.csv"

def scrape_authors():
    """
        Ambil list dosen yang terdaftar di Google Scholar berdasarkan GS_ORG_ID (UK Petra).
        Outputnya ditaruh di authors.csv
    """
    try:
        # Convert GS_ORG_ID to integer
        org_id = int(GS_ORG_ID)
        
        # Open CSV file for writing
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header row
            header = ['name', 'scholar_id', 'affiliation', 'email_domain', 'interests', 'citedby', 'url_picture']
            writer.writerow(header)
            f.flush()
            
            # Search for authors by organization ID
            print(f"Searching for authors in organization ID: {org_id}")
            search_query = scholarly.search_author_by_organization(org_id)
            
            count = 0
            for author in search_query:
                # Extract relevant fields (handling missing fields gracefully)
                row = [
                    author.get('name', ''),
                    author.get('scholar_id', ''),
                    author.get('affiliation', ''),
                    author.get('email_domain', ''),
                    ';'.join(author.get('interests', [])),
                    author.get('citedby', 0),
                    author.get('url_picture', '')
                ]
                
                # Write the row and flush
                writer.writerow(row)
                f.flush()
                
                count += 1
                if count % 10 == 0:
                    print(f"Scraped {count} authors so far...")
            
            print(f"Finished scraping. Total authors: {count}")
    
    except Exception as e:
        print(f"An error occurred: {e}")

# Execute the scraping function
if __name__ == "__main__":
    print("Starting author scraping...")
    scrape_authors()
    print(f"Results saved to {output_file}")
