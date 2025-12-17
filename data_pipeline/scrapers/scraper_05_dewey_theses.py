import requests
from bs4 import BeautifulSoup
import json
import os
import pandas as pd
import time
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from urllib.parse import urljoin
import random

# Thread lock for file operations
file_lock = threading.Lock()

def setup_output_directory(output_dir):
    """Create output directory if it doesn't exist"""
    os.makedirs(output_dir, exist_ok=True)

def load_thesis_ids(csv_path):
    """Load thesis IDs from the CSV file"""
    try:
        df = pd.read_csv(csv_path)
        return df['id'].astype(str).tolist()
    except Exception as e:
        print(f"Error loading thesis IDs: {e}")
        return []

def get_pending_ids(thesis_ids, output_dir):
    """Get list of IDs that haven't been scraped yet"""
    pending_ids = []
    for thesis_id in thesis_ids:
        json_path = os.path.join(output_dir, f"{thesis_id}.json")
        if not os.path.exists(json_path):
            pending_ids.append(thesis_id)
    return pending_ids

def clean_text(text):
    """Clean text by normalizing whitespace and removing extra spaces"""
    if not text:
        return ''
    # Replace multiple whitespace characters (including newlines) with single space
    cleaned = re.sub(r'\s+', ' ', text.strip())
    return cleaned

def extract_thesis_detail(soup, thesis_id):
    """Extract detailed thesis data from the thesis detail page"""
    try:
        viewer_content = soup.find('div', class_='viewer-content')
        if not viewer_content:
            return None

        # Initialize data with thesis ID
        data = {
            'id': thesis_id,
            'title': '',
            'abstract': '',
            'creators': '',
            'contributors': '',
            'publisher': '',
            'language': '',
            'theme': '',
            'category': '',
            'sub_category': '',
            'source': '',
            'subjects': ''
        }

        # Extract title (h3 element)
        title_element = viewer_content.find('h3')
        if title_element:
            data['title'] = clean_text(title_element.get_text(separator=' '))

        # Extract abstract (p element after h3)
        abstract_element = viewer_content.find('p')
        if abstract_element:
            data['abstract'] = clean_text(abstract_element.get_text(separator=' '))

        # Extract metadata from viewer-rows
        viewer_rows = viewer_content.find('div', class_='viewer-rows')
        if viewer_rows:
            labels = viewer_rows.find_all('label')
            for label in labels:
                label_text = label.get_text(strip=True).lower()
                span = label.find_next_sibling('span')
                if span:
                    value = clean_text(span.get_text(separator=' '))
                    
                    if label_text == 'creators':
                        data['creators'] = value
                    elif label_text == 'contributors':
                        data['contributors'] = value
                    elif label_text == 'publisher':
                        data['publisher'] = value
                    elif label_text == 'language':
                        data['language'] = value
                    elif label_text == 'theme':
                        data['theme'] = value
                    elif label_text == 'category':
                        data['category'] = value
                    elif label_text == 'sub category':
                        data['sub_category'] = value
                    elif label_text == 'source':
                        data['source'] = value
                    elif label_text == 'subjects':
                        data['subjects'] = value

        return data
    except Exception as e:
        print(f"Error extracting thesis detail for ID {thesis_id}: {e}")
        return None

def scrape_thesis_detail(thesis_id, session, base_url, max_retries=3):
    """Scrape detailed data for a single thesis with retry logic"""
    url = f"{base_url}/digital/view/{thesis_id}"
    
    for attempt in range(max_retries):
        try:
            # Add random delay to avoid overwhelming the server
            time.sleep(random.uniform(0.1, 0.5))
            
            response = session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            thesis_data = extract_thesis_detail(soup, thesis_id)
            
            if thesis_data:
                return thesis_data
            else:
                print(f"No data extracted for thesis ID {thesis_id}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed for thesis ID {thesis_id}: {e}")
            if attempt < max_retries - 1:
                time.sleep(random.uniform(1, 3))  # Wait before retry
            else:
                print(f"Failed to scrape thesis ID {thesis_id} after {max_retries} attempts")
                return None
        except Exception as e:
            print(f"Unexpected error scraping thesis ID {thesis_id}: {e}")
            return None

def save_thesis_json(thesis_data, output_dir):
    """Save thesis data to JSON file"""
    try:
        thesis_id = thesis_data['id']
        json_path = os.path.join(output_dir, f"{thesis_id}.json")
        
        with file_lock:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(thesis_data, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        print(f"Error saving thesis data: {e}")
        return False

def worker_scrape_theses(worker_id, thesis_ids, base_url, output_dir, session_headers):
    """Worker function to scrape a batch of thesis IDs"""
    session = requests.Session()
    session.headers.update(session_headers)
    
    print(f"Worker {worker_id}: Starting with {len(thesis_ids)} thesis IDs")
    
    successful_scrapes = 0
    failed_scrapes = 0
    
    for i, thesis_id in enumerate(thesis_ids):
        try:
            print(f"Worker {worker_id}: Scraping thesis {i+1}/{len(thesis_ids)} (ID: {thesis_id})")
            
            thesis_data = scrape_thesis_detail(thesis_id, session, base_url)
            
            if thesis_data:
                if save_thesis_json(thesis_data, output_dir):
                    successful_scrapes += 1
                    print(f"Worker {worker_id}: Successfully saved thesis ID {thesis_id}")
                else:
                    failed_scrapes += 1
                    print(f"Worker {worker_id}: Failed to save thesis ID {thesis_id}")
            else:
                failed_scrapes += 1
                print(f"Worker {worker_id}: Failed to scrape thesis ID {thesis_id}")
                
        except Exception as e:
            failed_scrapes += 1
            print(f"Worker {worker_id}: Unexpected error with thesis ID {thesis_id}: {e}")
    
    print(f"Worker {worker_id}: Completed. Successful: {successful_scrapes}, Failed: {failed_scrapes}")
    return successful_scrapes, failed_scrapes

def main():
    base_url = "https://dewey.petra.ac.id"
    csv_path = "../data/dewey_thesis_data.csv"
    output_dir = "../data/dewey_thesis"
    num_workers = 64
    
    # Setup
    setup_output_directory(output_dir)
    
    session_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Load thesis IDs from CSV
    print("Loading thesis IDs from CSV...")
    all_thesis_ids = load_thesis_ids(csv_path)
    
    if not all_thesis_ids:
        print("No thesis IDs found in CSV file")
        return
    
    print(f"Found {len(all_thesis_ids)} total thesis IDs")
    
    # Get pending IDs (not yet scraped)
    pending_ids = get_pending_ids(all_thesis_ids, output_dir)
    print(f"Found {len(pending_ids)} pending thesis IDs to scrape")
    
    if not pending_ids:
        print("All thesis IDs have already been scraped")
        return
    
    # Distribute IDs among workers
    ids_per_worker = len(pending_ids) // num_workers
    worker_batches = []
    
    for i in range(num_workers):
        start_idx = i * ids_per_worker
        if i == num_workers - 1:
            # Last worker gets remaining IDs
            end_idx = len(pending_ids)
        else:
            end_idx = (i + 1) * ids_per_worker
        
        if start_idx < len(pending_ids):
            worker_batches.append((i + 1, pending_ids[start_idx:end_idx]))
    
    print(f"Starting parallel scraping with {len(worker_batches)} workers")
    
    # Run workers in parallel
    total_successful = 0
    total_failed = 0
    
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = []
        for worker_id, batch_ids in worker_batches:
            if batch_ids:  # Only submit if there are IDs to process
                future = executor.submit(worker_scrape_theses, worker_id, batch_ids, base_url, output_dir, session_headers)
                futures.append(future)
        
        # Collect results
        for future in as_completed(futures):
            try:
                successful, failed = future.result()
                total_successful += successful
                total_failed += failed
            except Exception as e:
                print(f"Worker error: {e}")
                total_failed += 1
    
    # Final summary
    print(f"\nScraping completed!")
    print(f"Total successful: {total_successful}")
    print(f"Total failed: {total_failed}")
    print(f"JSON files saved to: {output_dir}")

if __name__ == "__main__":
    main()
