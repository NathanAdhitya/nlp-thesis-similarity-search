#!/usr/bin/env python3
"""
Test runner script for Semantica Integration Tests
"""
import os
import sys
import subprocess
import argparse

def run_behave_tests(tags=None, format_type="pretty", output_file=None):
    """
    Run Behave integration tests
    
    Args:
        tags (str): Behave tags to filter tests (e.g., "@smoke", "@regression")
        format_type (str): Output format (pretty, json, junit)
        output_file (str): Output file path for reports
    """
    
    # Change to project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    # Build behave command
    cmd = ["behave"]
    
    # Add format
    cmd.extend(["-f", format_type])
    
    # Add output file if specified
    if output_file:
        cmd.extend(["-o", output_file])
    
    # Add tags if specified
    if tags:
        cmd.extend(["--tags", tags])
    
    # Add features directory
    cmd.append("features")
    
    print(f"Running command: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        # Run the tests
        result = subprocess.run(cmd, capture_output=False, text=True)
        return result.returncode
    except FileNotFoundError:
        print("Error: Behave not found. Please install it using:")
        print("pip install -r test_requirements.txt")
        return 1
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1

def main():
    parser = argparse.ArgumentParser(description="Run Semantica Integration Tests")
    parser.add_argument("--tags", help="Behave tags to filter tests (e.g., @smoke)")
    parser.add_argument("--format", default="pretty", 
                       choices=["pretty", "json", "junit"],
                       help="Output format")
    parser.add_argument("--output", help="Output file for test reports")
    parser.add_argument("--install-deps", action="store_true",
                       help="Install test dependencies before running")
    
    args = parser.parse_args()
    
    # Install dependencies if requested
    if args.install_deps:
        print("Installing test dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "test_requirements.txt"])
        print("-" * 50)
    
    # Run tests
    exit_code = run_behave_tests(
        tags=args.tags,
        format_type=args.format,
        output_file=args.output
    )
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()