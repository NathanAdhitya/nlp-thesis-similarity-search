#!/usr/bin/env python3
"""Simple test runner for Behave"""
import os
import sys
import subprocess

def run_simple_test():
    """Run simple Behave test"""
    
    # Change to project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    print("Running simple Behave test...")
    print(f"Current directory: {os.getcwd()}")
    
    try:
        # Try running behave with python -m
        cmd = [sys.executable, "-m", "behave", "features/simple_test.feature", "-v"]
        print(f"Command: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=False, text=True)
        return result.returncode
        
    except Exception as e:
        print(f"Error: {e}")
        
        # Fallback: try direct behave command
        try:
            cmd = ["behave", "features/simple_test.feature", "-v"]
            print(f"Fallback command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=False, text=True)
            return result.returncode
        except Exception as e2:
            print(f"Fallback error: {e2}")
            return 1

if __name__ == "__main__":
    exit_code = run_simple_test()
    if exit_code == 0:
        print("\nSimple test passed!")
        print("You can now run full tests with: python -m behave")
    else:
        print(f"\nTest failed with exit code: {exit_code}")
    
    sys.exit(exit_code)