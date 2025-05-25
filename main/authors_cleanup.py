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
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, check=True)
        print(result.stdout)
        if result.stderr:
            print("Warnings/Errors:")
            print(result.stderr)
        print(f"✓ {description} completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error running {script_name}:")
        print(f"Exit code: {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False
    
    return True

def main():
    """Run the complete author cleanup pipeline."""
    print("Starting Complete Author Cleanup Pipeline")
    print("="*60)
    
    # Change to the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    steps = [
        # ("dewey_cleanup.py", "Dewey Thesis Author Cleanup and Clustering"),
        # ("scholar_cleanup.py", "Google Scholar Author Cleanup and Clustering"),
        # ("combine_authors.py", "Combining Dewey and Scholar Author Datasets"),
        ("merge_authors.py", "Merging Authors with ID Assignment"),
        ("extract_publications.py", "Extracting and Cleaning Publication Data"),
    ]
    
    success_count = 0
    
    for script, description in steps:
        if run_script(script, description):
            success_count += 1
        else:
            print(f"\n⚠️  Pipeline stopped due to error in {script}")
            print(f"Successfully completed: {success_count}/{len(steps)} steps")
            return False
    
    print(f"\n🎉 Pipeline completed successfully!")
    print(f"All {len(steps)} steps completed without errors")
    print("\nGenerated files:")
    print("- ../data/canonical_dewey.json")
    print("- ../data/canonical_scholar.json") 
    print("- ../data/combined_authors.json")
    print("- ../data/merged_authors.csv")
    print("- ../data/cleaned_dewey.csv")
    print("- ../data/cleaned_publications.csv")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
