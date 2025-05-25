import requests
from bs4 import BeautifulSoup
import csv
import os
import pandas as pd
import time
import re
from urllib.parse import urljoin, urlparse, parse_qs
from concurrent.futures import ThreadPoolExecutor
import threading

# Thread lock for CSV operations
csv_lock = threading.Lock()

def setup_csv_file(csv_path):
    """Initialize CSV file with headers if it doesn't exist"""
    if not os.path.exists(csv_path):
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        with open(csv_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['id', 'title', 'creator', 'contributor', 'publisher', 'source'])

def load_existing_data(csv_path):
    """Load existing data from CSV into a dictionary keyed by id"""
    existing_data = {}
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
            for _, row in df.iterrows():
                existing_data[str(row['id'])] = row.to_dict()
        except Exception as e:
            print(f"Error loading existing data: {e}")
    return existing_data

def save_data_to_csv(data_dict, csv_path):
    """Save the complete data dictionary to CSV"""
    df = pd.DataFrame.from_dict(data_dict, orient='index')
    df = df[['id', 'title', 'creator', 'contributor', 'publisher', 'source']]  # Ensure column order
    df.to_csv(csv_path, index=False, encoding='utf-8')

def extract_thesis_id(url):
    """Extract thesis ID from the detail page URL"""
    # URL format: https://dewey.petra.ac.id/digital/view/61082
    match = re.search(r'/view/(\d+)', url)
    return match.group(1) if match else None

def clean_text(text):
    """Clean text by normalizing whitespace and removing extra spaces"""
    if not text:
        return ''
    # Replace multiple whitespace characters (including newlines) with single space
    cleaned = re.sub(r'\s+', ' ', text.strip())
    return cleaned

def extract_thesis_data(li_element):
    """Extract thesis data from a single <li> element"""
    try:
        # Extract title and ID from the title link
        title_link = li_element.find('a', class_='title')
        if not title_link:
            return None
            
        # Use separator=' ' to preserve spaces between words when tags are present
        title = clean_text(title_link.get_text(separator=' '))
        thesis_id = extract_thesis_id(title_link['href'])
        
        if not thesis_id:
            return None

        # Extract info from the info-rows div
        info_rows = li_element.find('div', class_='info-rows')
        if not info_rows:
            return None

        # Initialize data with defaults
        data = {
            'id': thesis_id,
            'title': title,
            'creator': '',
            'contributor': '',
            'publisher': '',
            'source': ''
        }

        # Extract each field
        labels = info_rows.find_all('label')
        for label in labels:
            label_text = label.get_text(strip=True).lower()
            span = label.find_next_sibling('span')
            if span:
                # Use separator=' ' and clean the text
                value = clean_text(span.get_text(separator=' '))
                if label_text == 'creator':
                    data['creator'] = value
                elif label_text == 'contributor':
                    data['contributor'] = value
                elif label_text == 'publisher':
                    data['publisher'] = value
                elif label_text == 'source':
                    data['source'] = value

        return data
    except Exception as e:
        print(f"Error extracting thesis data: {e}")
        return None

def scrape_page(url, session):
    """Scrape a single page and return list of thesis data"""
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check if page is empty
        empty_collection = soup.find('div', class_='empty-collection-list')
        if empty_collection:
            return []

        # Find all thesis entries
        collection_list = soup.find('ul', class_='collection-list digital')
        if not collection_list:
            return []

        thesis_entries = collection_list.find_all('li') # type: ignore
        page_data = []
        
        for li in thesis_entries:
            thesis_data = extract_thesis_data(li)
            if thesis_data:
                page_data.append(thesis_data)
                
        return page_data
    except Exception as e:
        print(f"Error scraping page {url}: {e}")
        return []

def scrape_page_range(worker_id, start_page, end_page, base_url, csv_path, session_headers):
    """Scrape a range of pages for a single worker"""
    session = requests.Session()
    session.headers.update(session_headers)
    
    print(f"Worker {worker_id}: Starting pages {start_page} to {end_page}")
    
    # Load existing data for this worker
    with csv_lock:
        existing_data = load_existing_data(csv_path)
    
    worker_new_entries = 0
    worker_updated_entries = 0
    consecutive_empty_pages = 0
    
    for page in range(start_page, end_page + 1):
        if consecutive_empty_pages >= 5:
            print(f"Worker {worker_id}: Stopping due to 5 consecutive empty pages")
            break
            
        # Construct URL
        if page == 1:
            url = f"{base_url}?theme=2"
        else:
            url = f"{base_url}?theme=2&page={page}"
        
        print(f"Worker {worker_id}: Scraping page {page}...")
        
        page_data = scrape_page(url, session)
        
        if not page_data:
            consecutive_empty_pages += 1
            print(f"Worker {worker_id}: Empty page {page}. Consecutive empty: {consecutive_empty_pages}")
        else:
            consecutive_empty_pages = 0
            
            # Process each thesis entry
            page_updates = {}
            for thesis in page_data:
                thesis_id = thesis['id']
                page_updates[thesis_id] = thesis
                
                if thesis_id in existing_data:
                    worker_updated_entries += 1
                    print(f"Worker {worker_id}: Updated thesis ID: {thesis_id}")
                else:
                    worker_new_entries += 1
                    print(f"Worker {worker_id}: Added new thesis ID: {thesis_id}")
            
            # Thread-safe CSV update
            with csv_lock:
                current_data = load_existing_data(csv_path)
                current_data.update(page_updates)
                save_data_to_csv(current_data, csv_path)
                existing_data.update(page_updates)
            
            print(f"Worker {worker_id}: Saved {len(page_data)} entries from page {page}")
        
        time.sleep(0.5)  # Be respectful to the server
    
    print(f"Worker {worker_id}: Completed. New: {worker_new_entries}, Updated: {worker_updated_entries}")
    return worker_new_entries, worker_updated_entries

def main():
    base_url = "https://dewey.petra.ac.id/digital/browse"
    csv_path = "../data/dewey_thesis_data.csv"
    max_pages = 5000
    num_workers = 16
    
    # Setup
    setup_csv_file(csv_path)
    
    session_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    existing_data = load_existing_data(csv_path)
    print(f"Starting parallel scrape with {num_workers} workers. Existing entries: {len(existing_data)}")
    
    # Calculate page ranges for each worker
    pages_per_worker = max_pages // num_workers
    worker_ranges = []
    
    for i in range(num_workers):
        start_page = i * pages_per_worker + 1
        end_page = (i + 1) * pages_per_worker if i < num_workers - 1 else max_pages
        worker_ranges.append((i + 1, start_page, end_page))
    
    # Run workers in parallel
    total_new_entries = 0
    total_updated_entries = 0
    
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = []
        for worker_id, start_page, end_page in worker_ranges:
            future = executor.submit(scrape_page_range, worker_id, start_page, end_page, base_url, csv_path, session_headers)
            futures.append(future)
        
        # Collect results
        for future in futures:
            try:
                new_entries, updated_entries = future.result()
                total_new_entries += new_entries
                total_updated_entries += updated_entries
            except Exception as e:
                print(f"Worker error: {e}")
    
    # Final summary
    final_data = load_existing_data(csv_path)
    print(f"\nScraping completed!")
    print(f"Total entries: {len(final_data)}")
    print(f"New entries: {total_new_entries}")
    print(f"Updated entries: {total_updated_entries}")
    print(f"Data saved to: {csv_path}")

if __name__ == "__main__":
    main()
