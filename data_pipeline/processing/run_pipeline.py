"""
Main script to orchestrate the complete author cleanup and data extraction process.
"""

import subprocess
import sys
import os

def run_script(script_name, description):
    """Run a Python script and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Script: {script_name}")
    print(f"{'='*60}")
    
    # Build full path to script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, script_name)
    
    try:
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=True, text=True, check=True)
        print(result.stdout)
        if result.stderr:
            print("Warnings/Errors:")
            print(result.stderr)
        print(f"[OK] {description} completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error running {script_name}:")
        print(f"Exit code: {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False
    
    return True

def main():
    """Run the complete author cleanup pipeline."""
    print("Starting Complete Author Cleanup Pipeline")
    print("="*60)
    
    # Get the script directory for running sub-scripts
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    steps = [
        ("step_01_dewey_cleanup.py", "Dewey Thesis Author Cleanup and Clustering"),
        ("step_02_scholar_cleanup.py", "Google Scholar Author Cleanup and Clustering"),
        ("step_03_combine_authors.py", "Combining Dewey and Scholar Author Datasets"),
        ("step_04_merge_authors.py", "Merging Authors with ID Assignment"),
        ("step_05_extract_publications.py", "Extracting and Cleaning Publication Data"),
        ("step_06_create_database.py", "Creating SQLite Database"),
    ]
    
    success_count = 0
    
    for script, description in steps:
        if run_script(script, description):
            success_count += 1
        else:
            print(f"\n[WARNING] Pipeline stopped due to error in {script}")
            print(f"Successfully completed: {success_count}/{len(steps)} steps")
            return False
    
    print(f"\n[SUCCESS] Pipeline completed successfully!")
    print(f"All {len(steps)} steps completed without errors")
    print("\nGenerated files:")
    print("- data/canonical_dewey.json")
    print("- data/canonical_scholar.json") 
    print("- data/combined_authors.json")
    print("- data/merged_authors.csv")
    print("- data/cleaned_dewey.csv")
    print("- data/cleaned_publications.csv")
    print("- data/nlp-thesis-similarity-cleaned.db")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
